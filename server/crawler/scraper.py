from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class PageData:
    url: str
    final_url: str
    title: str
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class FetchResult:
    url: str
    status_code: int
    content_type: str
    html: str
    final_url: str


def fetch_html(
    url: str,
    *,
    timeout_s: float,
    user_agent: str,
    max_bytes: int,
) -> FetchResult:
    """Fetch HTML from a URL with a hard byte limit.

    Returns the initial URL, final URL after redirects, status code, content-type and decoded HTML.
    """
    headers = {"User-Agent": user_agent}
    with requests.get(url, headers=headers, timeout=timeout_s, stream=True, allow_redirects=True) as resp:
        status_code = resp.status_code
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        chunks: list[bytes] = []
        total = 0
        for chunk in resp.iter_content(chunk_size=65536):
            if not chunk:
                continue
            total += len(chunk)
            if total > max_bytes:
                break
            chunks.append(chunk)

        raw = b"".join(chunks)
        try:
            html = raw.decode(resp.encoding or "utf-8", errors="replace")
        except Exception:
            html = raw.decode("utf-8", errors="replace")
        return FetchResult(
            url=url,
            status_code=status_code,
            content_type=content_type,
            html=html,
            final_url=str(resp.url),
        )


def _strip_unwanted_nodes(soup: BeautifulSoup) -> None:
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()


def _extract_title(soup: BeautifulSoup) -> str:
    title_tag = soup.find("title")
    if title_tag and title_tag.get_text(strip=True):
        return title_tag.get_text(strip=True)

    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)

    return ""


def _extract_metadata(soup: BeautifulSoup, final_url: str) -> dict[str, Any]:
    meta: dict[str, Any] = {"final_url": final_url}
    description = soup.find("meta", attrs={"name": "description"})
    if description and description.get("content"):
        meta["description"] = str(description.get("content"))

    keywords = soup.find("meta", attrs={"name": "keywords"})
    if keywords and keywords.get("content"):
        meta["keywords"] = [k.strip() for k in str(keywords.get("content")).split(",") if k.strip()]

    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        meta["og:title"] = str(og_title.get("content"))

    return meta


def _extract_text(soup: BeautifulSoup) -> str:
    main = soup.find("main")
    root = main if main else soup.body if soup.body else soup
    text = root.get_text(" ", strip=True)
    return " ".join(text.split())


def scrape_html(html: str, *, url: str, final_url: str) -> PageData:
    """Extract a minimal, structured representation from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    _strip_unwanted_nodes(soup)
    title = _extract_title(soup)
    metadata = _extract_metadata(soup, final_url)
    text = _extract_text(soup)
    return PageData(url=url, final_url=final_url, title=title, text=text, metadata=metadata)


def normalize_link(base_url: str, href: Optional[str]) -> Optional[str]:
    if not href:
        return None
    href = href.strip()
    if href.startswith("#") or href.lower().startswith("javascript:"):
        return None
    return urljoin(base_url, href)

