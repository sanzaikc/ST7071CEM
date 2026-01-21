"""Approach to Pure Portal crawling"""
import asyncio
import re
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse, urlunparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from crawler.config import settings
from crawler.robots import robots_allows, robots_txt_url
from crawler.events import emit_crawl_event
from database.repositories import (
    upsert_publication_by_pure_id,
    upsert_author_by_pure_id,
    increment_author_publication_count,
    update_crawl_job_status,
    update_crawl_job_stats,
    add_crawl_job_error
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


def init_selenium_driver():
    """Initialize headless Chrome driver"""
    logger.info("Initializing Chrome driver...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={settings.user_agent}")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    logger.info("Chrome driver initialized")
    return driver


def close_selenium_driver(driver):
    """Close Chrome driver"""
    if driver:
        driver.quit()
        logger.info("Chrome driver closed")


async def apply_polite_delay(url: str, robots_parser_cache: Dict):
    """Apply polite crawl delay"""
    delay = settings.crawl_delay
    
    # Check if robots.txt specifies a different delay
    if url and settings.respect_robots_txt:
        robots_url = robots_txt_url(url)
        if robots_url in robots_parser_cache:
            parser = robots_parser_cache[robots_url]
            robot_delay = parser.crawl_delay(settings.user_agent.split()[0] or "*")
            if robot_delay:
                delay = max(delay, robot_delay)
    
    await asyncio.sleep(delay)


def can_crawl_url(url: str, robots_parser_cache: Dict) -> bool:
    """Check if URL can be crawled according to robots.txt"""
    if not settings.respect_robots_txt:
        return True
    
    return robots_allows(
        url,
        user_agent=settings.user_agent,
        timeout_s=settings.crawl_timeout,
        max_bytes=2_000_000,
        robots_parser_cache=robots_parser_cache
    )


def extract_pure_id(url: str) -> Optional[str]:
    """Extract Pure ID from URL"""
    match = re.search(r"/publications/([a-zA-Z0-9-]+)", url)
    if match:
        return match.group(1)
    
    match = re.search(r"/persons/([a-zA-Z0-9-]+)", url)
    if match:
        return match.group(1)
    
    return None


def _canonicalize_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = (parsed.scheme or "https").lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))


def _as_absolute_url(base_url: str, href: str) -> Optional[str]:
    if not href:
        return None
    return _canonicalize_url(urljoin(base_url, href))


def _iter_candidate_org_urls() -> List[str]:
    urls: List[str] = []

    def add(u: str):
        cu = _canonicalize_url(u)
        if cu not in urls:
            urls.append(cu)

    target = settings.target_url
    trimmed = target.rstrip("/")
    if trimmed.endswith("/publications"):
        add(trimmed[: -len("/publications")])
    add(target)

    for candidate in list(urls):
        if "researchcentre" in candidate:
            add(candidate.replace("researchcentre", "research-centre"))
        if "research-centre" in candidate:
            add(candidate.replace("research-centre", "researchcentre"))

    return urls


def _author_publications_url(profile_url: str) -> str:
    base = profile_url.rstrip("/")
    return _canonicalize_url(f"{base}/publications/")


def _find_next_page_url(soup: BeautifulSoup, current_url: str) -> Optional[str]:
    link = soup.find("a", attrs={"rel": lambda v: v and "next" in v})
    if link and link.get("href"):
        return _as_absolute_url(current_url, link.get("href"))

    link = soup.find("a", attrs={"aria-label": re.compile(r"\bnext\b", re.I)})
    if link and link.get("href"):
        return _as_absolute_url(current_url, link.get("href"))

    for a in soup.find_all("a", href=True):
        if a.get_text(strip=True).lower() == "next":
            return _as_absolute_url(current_url, a.get("href"))

    return None


def is_page_blocked(driver, soup) -> bool:
    """Check if the page is blocked by Cloudflare or other protection"""
    text = soup.get_text()
    if "Verify you are human" in text or "Just a moment..." in driver.title:
        return True
    return False


async def scrape_publications_from_profile(driver, profile_url: str, job_id: str, author_data: Dict) -> List[Dict[str, Any]]:
    """Fallback: Scrape publications directly from the author's profile page"""
    logger.info(f"Fallback: Scraping publications from profile page: {profile_url}")
    publications = []
    
    try:
        driver.get(profile_url)
        await asyncio.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        if is_page_blocked(driver, soup):
             logger.error(f"Profile page also blocked for {author_data.get('name')}")
             return []
             
        # Look for publication links
        all_links = soup.find_all("a", href=re.compile(r"/publications/"))
        seen_urls = set()
        
        for link in all_links:
            href = link.get("href")
            pub_url = _as_absolute_url(profile_url, href)
            
            if not pub_url:
                continue
                
            # Filter out the "Publications" tab link itself or other non-publication links
            # We want links that look like .../publications/some-title
            # And avoid .../persons/.../publications/
            if "/persons/" in pub_url:
                continue
            
            # If it ends with /publications/ or /publications, it's likely a list page
            if pub_url.rstrip("/").endswith("/publications"):
                continue

            if pub_url in seen_urls:
                continue
                
            seen_urls.add(pub_url)
            publications.append({"publication_url": pub_url})
            
        if publications:
            logger.info(f"Found {len(publications)} publications on profile page for {author_data.get('name')}")
            await emit_crawl_event(
                job_id,
                stage="fallback_profile_scrape",
                message=f"Found {len(publications)} publications on profile page (fallback)",
                data={"author": author_data.get("name"), "count": len(publications)}
            )
            
    except Exception as e:
        logger.error(f"Error in fallback profile scrape: {e}")
        
    return publications


async def crawl_researchers(driver, robots_parser_cache: Dict, job_id: str) -> List[Dict[str, Any]]:
    """Crawl researcher profiles from department page"""
    target_urls = _iter_candidate_org_urls()
    logger.info(f"Crawling researchers from: {target_urls[0]}")

    researchers: List[Dict[str, Any]] = []
    seen_profile_urls: set[str] = set()

    for target_url in target_urls:
        if not can_crawl_url(target_url, robots_parser_cache):
            logger.error(f"robots.txt disallows crawling the target URL: {target_url}")
            await emit_crawl_event(
                job_id,
                stage="robots_blocked",
                message="robots.txt blocked organisation page",
                level="warn",
                url=target_url,
            )
            continue

        try:
            await emit_crawl_event(
                job_id,
                stage="fetch_organisation",
                message="Fetching organisation page",
                url=target_url,
            )
            driver.get(target_url)
            await apply_polite_delay(target_url, robots_parser_cache)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")

            if is_page_blocked(driver, soup):
                logger.warning(f"Organisation page blocked: {target_url}")
                continue

            person_links = soup.find_all("a", href=re.compile(r"/persons/"))

            for link in person_links:
                href = link.get("href")
                profile_url = _as_absolute_url(target_url, href) if href else None
                if not profile_url or profile_url in seen_profile_urls:
                    continue

                name = link.get_text(strip=True)
                if not name:
                    continue

                pure_id = extract_pure_id(profile_url)
                if not pure_id:
                    continue

                researcher = {
                    "name": name,
                    "profile_url": profile_url,
                    "pure_id": pure_id,
                    "department": "Research Centre for Computational Science and Mathematical Modelling",
                }
                researchers.append(researcher)
                seen_profile_urls.add(profile_url)

            if researchers:
                break

        except Exception as e:
            logger.error(f"Error crawling researchers ({target_url}): {e}")
            await emit_crawl_event(
                job_id,
                stage="fetch_organisation_error",
                message=str(e),
                level="error",
                url=target_url,
            )

    logger.info(f"Found {len(researchers)} researchers")
    await emit_crawl_event(
        job_id,
        stage="discover_researchers",
        message=f"Discovered {len(researchers)} researchers",
        counters={"authors_crawled": len(researchers)},
    )
    return researchers


async def crawl_author_publications(
    driver,
    author: Dict[str, Any],
    robots_parser_cache: Dict,
    job_id: str,
) -> List[Dict[str, Any]]:
    """Crawl publications from an author's profile"""
    logger.info(f"Crawling publications for: {author['name']}")

    profile_url = author["profile_url"]
    publications_url = _author_publications_url(profile_url)

    if not can_crawl_url(publications_url, robots_parser_cache):
        logger.warning(f"Skipping author (robots.txt): {author['name']}")
        await emit_crawl_event(
            job_id,
            stage="robots_blocked",
            message="robots.txt blocked author publications listing",
            level="warn",
            url=publications_url,
            data={"author": author.get("name"), "author_pure_id": author.get("pure_id")},
        )
        return []

    publications: List[Dict[str, Any]] = []
    seen_publication_urls: set[str] = set()
    seen_pages: set[str] = set()

    current_url: Optional[str] = publications_url
    pages = 0

    try:
        while current_url and current_url not in seen_pages and pages < 100:
            if not can_crawl_url(current_url, robots_parser_cache):
                break

            seen_pages.add(current_url)
            pages += 1

            await emit_crawl_event(
                job_id,
                stage="fetch_author_publications_page",
                message="Fetching author publications page",
                url=current_url,
                data={"author": author.get("name"), "author_pure_id": author.get("pure_id"), "page": pages},
            )
            driver.get(current_url)
            await apply_polite_delay(current_url, robots_parser_cache)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")

            if is_page_blocked(driver, soup):
                logger.warning(f"Blocked on author publications page for {author['name']}")
                if pages == 1:
                    return await scrape_publications_from_profile(driver, profile_url, job_id, author)
                else:
                    break

            pub_links = soup.find_all("a", href=re.compile(r"/publications/"))

            for link in pub_links:
                href = link.get("href")
                pub_url = _as_absolute_url(driver.current_url, href) if href else None
                if not pub_url or pub_url in seen_publication_urls:
                    continue

                seen_publication_urls.add(pub_url)
                publications.append({"publication_url": pub_url})

            current_url = _find_next_page_url(soup, current_url)

        logger.info(f"Found {len(publications)} publications for {author['name']}")
        await emit_crawl_event(
            job_id,
            stage="list_author_publications_done",
            message=f"Collected {len(publications)} publications for author",
            counters={"publication_urls_collected": len(publications)},
            data={"author": author.get("name"), "author_pure_id": author.get("pure_id")},
        )

    except Exception as e:
        logger.error(f"Error crawling author publications: {e}")
        await emit_crawl_event(
            job_id,
            stage="list_author_publications_error",
            message=str(e),
            level="error",
            url=publications_url,
            data={"author": author.get("name"), "author_pure_id": author.get("pure_id")},
        )

    return publications


async def crawl_publication_details(
    driver,
    pub_url: str,
    robots_parser_cache: Dict,
    job_id: str,
) -> Optional[Dict[str, Any]]:
    """Crawl detailed information from a publication page"""
    logger.info(f"Crawling publication: {pub_url}")
    
    if not can_crawl_url(pub_url, robots_parser_cache):
        logger.warning(f"Skipping publication (robots.txt): {pub_url}")
        await emit_crawl_event(
            job_id,
            stage="robots_blocked",
            message="robots.txt blocked publication page",
            level="warn",
            url=pub_url,
        )
        return None
    
    try:
        await emit_crawl_event(
            job_id,
            stage="fetch_publication",
            message="Fetching publication page",
            url=pub_url,
        )
        driver.get(pub_url)
        await apply_polite_delay(pub_url, robots_parser_cache)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract publication details
        publication = {
            "pure_id": extract_pure_id(pub_url) or pub_url.split('/')[-1],
            "publication_url": pub_url,
            "title": "",
            "authors": [],
            "year": 0,
            "publication_type": "other",
            "abstract": "",
            "keywords": [],
            "doi": None,
            "external_url": None
        }
        
        # Title
        title_elem = soup.find('h1')
        if title_elem:
            publication["title"] = title_elem.get_text(strip=True)
        
        author_links = soup.find_all("a", href=re.compile(r"/persons/"))
        seen_author_ids: set[str] = set()
        for link in author_links:
            author_name = link.get_text(strip=True)
            author_url = link.get("href")
            abs_author_url = _as_absolute_url(pub_url, author_url) if author_url else None
            author_id = extract_pure_id(abs_author_url or "")
            if not author_id or author_id in seen_author_ids:
                continue
            seen_author_ids.add(author_id)
            publication["authors"].append(
                {
                    "name": author_name,
                    "profile_url": abs_author_url,
                    "pure_id": author_id,
                }
            )

        year = 0
        for meta_name in (
            "citation_publication_date",
            "citation_date",
            "citation_year",
            "dc.date",
            "dcterms.issued",
        ):
            meta = soup.find("meta", attrs={"name": meta_name})
            content = meta.get("content") if meta else None
            if content:
                m = re.search(r"\b(19|20)\d{2}\b", content)
                if m:
                    year = int(m.group())
                    break

        if not year:
            m = re.search(r"\b(19|20)\d{2}\b", soup.get_text(" ", strip=True))
            if m:
                year = int(m.group())

        publication["year"] = year
        
        # Abstract
        abstract_elem = soup.find(['div', 'p'], class_=re.compile(r'abstract', re.I))
        if abstract_elem:
            publication["abstract"] = abstract_elem.get_text(strip=True)
        
        # DOI
        doi_link = soup.find('a', href=re.compile(r'doi\.org'))
        if doi_link:
            publication["doi"] = doi_link.get('href')
        
        # Publication type
        if '/publications/' in pub_url:
            page_text = soup.get_text().lower()
            if 'journal' in page_text:
                publication["publication_type"] = "journal_article"
            elif 'conference' in page_text:
                publication["publication_type"] = "conference_paper"
            elif 'book' in page_text:
                publication["publication_type"] = "book"
        
        logger.info(f"Extracted publication: {publication['title']}")
        await emit_crawl_event(
            job_id,
            stage="extract_publication",
            message="Extracted publication metadata",
            url=pub_url,
            data={
                "pure_id": publication.get("pure_id"),
                "title": publication.get("title"),
                "year": publication.get("year"),
                "authors_count": len(publication.get("authors") or []),
            },
        )
        return publication
        
    except Exception as e:
        logger.error(f"Error crawling publication details: {e}")
        await emit_crawl_event(
            job_id,
            stage="fetch_publication_error",
            message=str(e),
            level="error",
            url=pub_url,
        )
        return None


async def run_full_crawl(job_id: str):
    """Run full crawl of all researchers and publications"""
    logger.info("Starting full crawl...")
    
    driver = None
    robots_parser_cache = {}
    stats = {
        "authors_crawled": 0,
        "publications_found": 0,
        "new_publications": 0,
        "updated_publications": 0,
        "errors": 0
    }
    
    try:
        # Initialize driver
        driver = init_selenium_driver()
        
        # Update job status
        await update_crawl_job_status(job_id, "running")
        await emit_crawl_event(job_id, stage="job_started", message="Crawl started", counters=stats)

        researchers = await crawl_researchers(driver, robots_parser_cache, job_id)

        if not researchers:
            logger.warning("No researchers found!")
            await update_crawl_job_status(job_id, "completed")
            await update_crawl_job_stats(job_id, stats)
            return

        member_pure_ids: set[str] = {r["pure_id"] for r in researchers if r.get("pure_id")}

        for researcher in researchers:
            try:
                await upsert_author_by_pure_id(researcher)
                stats["authors_crawled"] += 1
                await emit_crawl_event(
                    job_id,
                    stage="persist_author",
                    message="Saved author profile",
                    counters=stats,
                    data={"author": researcher.get("name"), "author_pure_id": researcher.get("pure_id")},
                )
            except Exception as e:
                logger.error(f"Error saving author: {e}")
                stats["errors"] += 1
                await emit_crawl_event(
                    job_id,
                    stage="persist_author_error",
                    message=str(e),
                    level="error",
                    counters=stats,
                    data={"author": researcher.get("name"), "author_pure_id": researcher.get("pure_id")},
                )

        publication_url_set: set[str] = set()

        for researcher in researchers:
            try:
                pub_list = await crawl_author_publications(driver, researcher, robots_parser_cache, job_id)
                for p in pub_list:
                    u = p.get("publication_url")
                    if u:
                        publication_url_set.add(_canonicalize_url(u))
            except Exception as e:
                logger.error(f"Error processing researcher {researcher['name']}: {e}")
                await add_crawl_job_error(job_id, str(e))
                stats["errors"] += 1
                await emit_crawl_event(
                    job_id,
                    stage="list_author_publications_error",
                    message=str(e),
                    level="error",
                    counters=stats,
                    data={"author": researcher.get("name"), "author_pure_id": researcher.get("pure_id")},
                )

        publication_urls = list(publication_url_set)
        logger.info(f"Collected {len(publication_urls)} unique publication URLs from department members")
        await emit_crawl_event(
            job_id,
            stage="collect_publication_urls_done",
            message=f"Collected {len(publication_urls)} unique publication URLs",
            counters={**stats, "publication_urls_total": len(publication_urls)},
        )
        
        # Step 3: Crawl each publication's details
        logger.info(f"Crawling {len(publication_urls)} publications...")
        
        for idx, pub_url in enumerate(publication_urls, start=1):
            try:
                await emit_crawl_event(
                    job_id,
                    stage="crawl_progress",
                    message="Processing publication",
                    url=pub_url,
                    counters={**stats, "publications_processed": idx, "publication_urls_total": len(publication_urls)},
                )
                pub_details = await crawl_publication_details(driver, pub_url, robots_parser_cache, job_id)

                if not pub_details or not pub_details.get("title"):
                    continue

                if not any(a.get("pure_id") in member_pure_ids for a in pub_details.get("authors") or []):
                    await emit_crawl_event(
                        job_id,
                        stage="skip_publication",
                        message="Skipped publication (no department co-author found)",
                        level="warn",
                        url=pub_url,
                        counters={**stats, "publications_processed": idx, "publication_urls_total": len(publication_urls)},
                    )
                    continue

                _, is_new = await upsert_publication_by_pure_id(pub_details)

                stats["publications_found"] += 1
                if is_new:
                    stats["new_publications"] += 1
                else:
                    stats["updated_publications"] += 1

                for author in pub_details["authors"]:
                    if author.get("pure_id") in member_pure_ids:
                        await increment_author_publication_count(author["pure_id"])

                await emit_crawl_event(
                    job_id,
                    stage="persist_publication",
                    message="Saved publication",
                    url=pub_url,
                    counters={**stats, "publications_processed": idx, "publication_urls_total": len(publication_urls)},
                    data={"pure_id": pub_details.get("pure_id"), "title": pub_details.get("title"), "is_new": is_new},
                )
            
            except Exception as e:
                logger.error(f"Error processing publication {pub_url}: {e}")
                await add_crawl_job_error(job_id, str(e))
                stats["errors"] += 1
                await emit_crawl_event(
                    job_id,
                    stage="persist_publication_error",
                    message=str(e),
                    level="error",
                    url=pub_url,
                    counters={**stats, "publications_processed": idx, "publication_urls_total": len(publication_urls)},
                )
        
        # Update job completion
        await update_crawl_job_status(job_id, "completed")
        await update_crawl_job_stats(job_id, stats)
        await emit_crawl_event(job_id, stage="job_completed", message="Crawl completed", counters=stats)
        
        logger.info(f"Crawl completed. Stats: {stats}")
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}")
        await update_crawl_job_status(job_id, "failed")
        await add_crawl_job_error(job_id, str(e))
        stats["errors"] += 1
        await update_crawl_job_stats(job_id, stats)
        await emit_crawl_event(job_id, stage="job_failed", message=str(e), level="error", counters=stats)
    
    finally:
        if driver:
            close_selenium_driver(driver)
