from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Optional

import requests
from fastapi import HTTPException

from crawler.config import settings
from crawler.robots import robots_allows
from crawler.scraper import fetch_html, scrape_html
from database.documents import upsert_document, upsert_postings
from indexing.text import l2_norm, term_frequencies, tokenize, vector_weights


@dataclass(frozen=True)
class CrawlOptions:
    respect_robots_txt: bool = False
    timeout_s: float = 30.0
    user_agent: str = "CU-Research-SearchBot/1.0"
    max_bytes: int = 2_000_000


@dataclass(frozen=True)
class CrawlStoredResult:
    url: str
    final_url: str
    title: str
    tokens: int
    stored_document_id: Any


async def _fetch_and_scrape(url: str, *, options: CrawlOptions):
    return await asyncio.to_thread(
        lambda: scrape_html(
            fetch_html(
                url,
                timeout_s=options.timeout_s,
                user_agent=options.user_agent,
                max_bytes=options.max_bytes,
            ).html,
            url=url,
            final_url=url,
        )
    )


async def crawl_url_and_index(db, *, url: str, options: Optional[CrawlOptions] = None) -> CrawlStoredResult:
    """Crawl a single URL, store the document, and update the inverted index.

    Args:
        db: MongoDB database handle (Motor).
        url: Target URL.
        options: Crawl options. If not provided, defaults are derived from settings.

    Returns:
        CrawlStoredResult for the stored document.

    Raises:
        HTTPException: For HTTP and parsing errors with appropriate status codes.
    """

    opts = options or CrawlOptions(
        respect_robots_txt=settings.respect_robots_txt,
        timeout_s=float(settings.crawl_timeout),
        user_agent=settings.user_agent,
        max_bytes=int(getattr(settings, "crawl_max_bytes", 2_000_000)),
    )

    robots_decision = robots_allows(
        url,
        respect_robots_txt=opts.respect_robots_txt,
        timeout_s=opts.timeout_s,
        user_agent=opts.user_agent,
        max_bytes=min(opts.max_bytes, 200_000),
    )
    if not robots_decision.allowed:
        raise HTTPException(status_code=403, detail=f"Crawl blocked: {robots_decision.reason}")

    try:
        fetch_result = await asyncio.to_thread(
            lambda: fetch_html(
                url,
                timeout_s=opts.timeout_s,
                user_agent=opts.user_agent,
                max_bytes=opts.max_bytes,
            )
        )
        page = await asyncio.to_thread(
            lambda: scrape_html(fetch_result.html, url=url, final_url=fetch_result.final_url)
        )
    except requests.HTTPError as e:
        status_code = int(getattr(getattr(e, "response", None), "status_code", 502) or 502)
        raise HTTPException(status_code=status_code, detail=f"Fetch failed: {status_code}")
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Fetch failed: upstream error")
    except Exception:
        raise HTTPException(status_code=500, detail="Scrape failed")

    tokens = tokenize(f"{page.title} {page.text}")
    tf = term_frequencies(tokens)
    weights = vector_weights(tf)
    norm = l2_norm(weights)

    stored = await upsert_document(
        db,
        url=page.url,
        title=page.title,
        text=page.text,
        metadata=page.metadata,
        term_weights=weights,
        norm=norm,
    )
    await upsert_postings(db, doc_id=stored.id, term_weights=weights)

    return CrawlStoredResult(
        url=page.url,
        final_url=page.final_url,
        title=page.title,
        tokens=len(tokens),
        stored_document_id=stored.id,
    )

