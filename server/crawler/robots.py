from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser

import requests


@dataclass(frozen=True)
class RobotsDecision:
    allowed: bool
    reason: str


def robots_txt_url(target_url: str) -> str:
    """Return the robots.txt URL for a given target URL."""
    parsed = urlparse(target_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    return urljoin(base, "/robots.txt")


def build_robot_parser(robots_txt_url_value: str, robots_txt: str) -> RobotFileParser:
    parser = RobotFileParser()
    parser.set_url(robots_txt_url_value)
    parser.parse(robots_txt.splitlines())
    return parser


def fetch_robots_txt(
    target_url: str,
    *,
    timeout_s: float,
    user_agent: str,
    max_bytes: int,
) -> tuple[str, Optional[str]]:
    url = robots_txt_url(target_url)
    headers = {"User-Agent": user_agent}

    try:
        with requests.get(url, headers=headers, timeout=timeout_s, stream=True) as resp:
            resp.raise_for_status()
            chunks: list[bytes] = []
            total = 0
            for chunk in resp.iter_content(chunk_size=16384):
                if not chunk:
                    continue
                total += len(chunk)
                if total > max_bytes:
                    break
                chunks.append(chunk)
            
            content = b"".join(chunks).decode("utf-8", errors="replace")
            return url, content
    except Exception:
        return url, None


def robots_allows(
    target_url: str,
    *,
    user_agent: str,
    timeout_s: float,
    max_bytes: int,
    robots_parser_cache: Dict[str, RobotFileParser]
) -> bool:
    """Check if robots.txt allows crawling the target URL with caching"""
    robots_url = robots_txt_url(target_url)

    if robots_url in robots_parser_cache:
        parser = robots_parser_cache[robots_url]
        return parser.can_fetch(user_agent.split()[0] or "*", target_url)

    _, robots_content = fetch_robots_txt(
        target_url,
        timeout_s=timeout_s,
        user_agent=user_agent,
        max_bytes=max_bytes,
    )

    if not robots_content:
        return True

    parser = build_robot_parser(robots_url, robots_content)
    robots_parser_cache[robots_url] = parser

    return parser.can_fetch(user_agent.split()[0] or "*", target_url)

