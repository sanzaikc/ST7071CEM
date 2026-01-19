"""Functional approach to Pure Portal crawling - replaces pureportal_crawler.py class"""
import time
import re
from typing import List, Dict, Any, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from crawler.config import settings
from crawler.robots import robots_allows, fetch_robots_txt, build_robot_parser, robots_txt_url
from crawler.sitemap import parse_sitemap, filter_urls_by_pattern
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


def apply_polite_delay(url: str, robots_parser_cache: Dict):
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
    
    time.sleep(delay)


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
    # Example URL: https://pureportal.coventry.ac.uk/en/publications/some-id
    match = re.search(r'/publications/([a-zA-Z0-9-]+)', url)
    if match:
        return match.group(1)
    
    # Try persons URL
    match = re.search(r'/persons/([a-zA-Z0-9-]+)', url)
    if match:
        return match.group(1)
    
    return None


def get_robots_sitemaps(target_url: str) -> List[str]:
    """Extract sitemap URLs from robots.txt"""
    try:
        robots_url = robots_txt_url(target_url)
        response_url, robots_content = fetch_robots_txt(
            target_url,
            timeout_s=settings.crawl_timeout,
            user_agent=settings.user_agent,
            max_bytes=2_000_000
        )
        
        if not robots_content:
            return []
        
        sitemaps = []
        for line in robots_content.split('\n'):
            line = line.strip()
            if line.lower().startswith('sitemap:'):
                sitemap_url = line.split(':', 1)[1].strip()
                sitemaps.append(sitemap_url)
                logger.info(f"Found sitemap: {sitemap_url}")
        
        return sitemaps
    except Exception as e:
        logger.warning(f"Failed to extract sitemaps: {e}")
        return []


async def crawl_researchers(driver, robots_parser_cache: Dict) -> List[Dict[str, Any]]:
    """Crawl researcher profiles from department page"""
    target_url = settings.target_url
    logger.info(f"Crawling researchers from: {target_url}")
    
    if not can_crawl_url(target_url, robots_parser_cache):
        logger.error("robots.txt disallows crawling the target URL")
        return []
    
    researchers = []
    
    try:
        driver.get(target_url)
        apply_polite_delay(target_url, robots_parser_cache)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find researcher links
        person_links = soup.find_all('a', href=re.compile(r'/en/persons/'))
        
        for link in person_links:
            href = link.get('href')
            if href:
                # Make absolute URL
                if href.startswith('/'):
                    profile_url = f"https://pureportal.coventry.ac.uk{href}"
                else:
                    profile_url = href
                
                # Extract name
                name = link.get_text(strip=True)
                
                if name and profile_url not in [r['profile_url'] for r in researchers]:
                    pure_id = extract_pure_id(profile_url)
                    if pure_id:
                        researcher = {
                            "name": name,
                            "profile_url": profile_url,
                            "pure_id": pure_id,
                            "department": "Research Centre for Computational Science and Mathematical Modelling"
                        }
                        researchers.append(researcher)
                        logger.info(f"Found researcher: {name}")
        
        logger.info(f"Found {len(researchers)} researchers")
        
    except Exception as e:
        logger.error(f"Error crawling researchers: {e}")
    
    return researchers


async def crawl_author_publications(
    driver,
    author: Dict[str, Any],
    robots_parser_cache: Dict
) -> List[Dict[str, Any]]:
    """Crawl publications from an author's profile"""
    logger.info(f"Crawling publications for: {author['name']}")
    
    profile_url = author['profile_url']
    
    if not can_crawl_url(profile_url, robots_parser_cache):
        logger.warning(f"Skipping author (robots.txt): {author['name']}")
        return []
    
    publications = []
    
    try:
        driver.get(profile_url)
        apply_polite_delay(profile_url, robots_parser_cache)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find publication links
        pub_links = soup.find_all('a', href=re.compile(r'/en/publications/'))
        
        for link in pub_links:
            href = link.get('href')
            if href:
                if href.startswith('/'):
                    pub_url = f"https://pureportal.coventry.ac.uk{href}"
                else:
                    pub_url = href
                
                # Avoid duplicates
                if pub_url not in [p['publication_url'] for p in publications]:
                    publications.append({'publication_url': pub_url})
        
        logger.info(f"Found {len(publications)} publications for {author['name']}")
        
    except Exception as e:
        logger.error(f"Error crawling author publications: {e}")
    
    return publications


async def crawl_publication_details(
    driver,
    pub_url: str,
    robots_parser_cache: Dict
) -> Optional[Dict[str, Any]]:
    """Crawl detailed information from a publication page"""
    logger.info(f"Crawling publication: {pub_url}")
    
    if not can_crawl_url(pub_url, robots_parser_cache):
        logger.warning(f"Skipping publication (robots.txt): {pub_url}")
        return None
    
    try:
        driver.get(pub_url)
        apply_polite_delay(pub_url, robots_parser_cache)
        
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
        
        # Authors
        author_links = soup.find_all('a', href=re.compile(r'/en/persons/'))
        for link in author_links:
            author_name = link.get_text(strip=True)
            author_url = link.get('href')
            if author_url and author_url.startswith('/'):
                author_url = f"https://pureportal.coventry.ac.uk{author_url}"
            
            author_id = extract_pure_id(author_url)
            if author_id:
                publication["authors"].append({
                    "name": author_name,
                    "profile_url": author_url,
                    "pure_id": author_id
                })
        
        # Year
        year_match = re.search(r'\b(19|20)\d{2}\b', soup.get_text())
        if year_match:
            publication["year"] = int(year_match.group())
        
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
        return publication
        
    except Exception as e:
        logger.error(f"Error crawling publication details: {e}")
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
        
        # Step 1: Check for sitemaps first
        logger.info("Checking for sitemaps in robots.txt...")
        sitemaps = get_robots_sitemaps(settings.target_url)
        
        publication_urls = []
        
        if sitemaps:
            logger.info(f"Found {len(sitemaps)} sitemap(s), extracting URLs...")
            
            for sitemap_url in sitemaps:
                # Parse sitemap
                sitemap_urls = parse_sitemap(sitemap_url, timeout=settings.crawl_timeout)
                
                # Filter for publication/project URLs
                pub_urls = filter_urls_by_pattern(sitemap_urls, '/publications/')
                project_urls = filter_urls_by_pattern(sitemap_urls, '/projects/')
                
                # Combine publication URLs
                publication_urls.extend([url['loc'] for url in pub_urls])
                publication_urls.extend([url['loc'] for url in project_urls])
            
            logger.info(f"Found {len(publication_urls)} publication/project URLs from sitemaps")
        
        # Step 2: If no sitemap URLs, fall back to crawling researchers
        if not publication_urls:
            logger.info("No sitemap URLs found, crawling researchers...")
            researchers = await crawl_researchers(driver, robots_parser_cache)
            
            if not researchers:
                logger.warning("No researchers found!")
                await update_crawl_job_status(job_id, "completed")
                await update_crawl_job_stats(job_id, stats)
                return
            
            # Save authors to database
            for researcher in researchers:
                try:
                    await upsert_author_by_pure_id(researcher)
                    stats["authors_crawled"] += 1
                except Exception as e:
                    logger.error(f"Error saving author: {e}")
                    stats["errors"] += 1
            
            # Get publication URLs from each researcher
            for researcher in researchers:
                try:
                    pub_list = await crawl_author_publications(driver, researcher, robots_parser_cache)
                    publication_urls.extend([p['publication_url'] for p in pub_list])
                except Exception as e:
                    logger.error(f"Error processing researcher {researcher['name']}: {e}")
                    await add_crawl_job_error(job_id, str(e))
                    stats["errors"] += 1
        
        # Step 3: Crawl each publication's details
        logger.info(f"Crawling {len(publication_urls)} publications...")
        
        for pub_url in publication_urls:
            try:
                pub_details = await crawl_publication_details(driver, pub_url, robots_parser_cache)
                
                if pub_details and pub_details.get('title'):
                    # Save to database
                    doc_id, is_new = await upsert_publication_by_pure_id(pub_details)
                    
                    stats["publications_found"] += 1
                    if is_new:
                        stats["new_publications"] += 1
                    else:
                        stats["updated_publications"] += 1
                    
                    # Update author publication counts
                    for author in pub_details["authors"]:
                        await increment_author_publication_count(author["pure_id"])
            
            except Exception as e:
                logger.error(f"Error processing publication {pub_url}: {e}")
                await add_crawl_job_error(job_id, str(e))
                stats["errors"] += 1
        
        # Update job completion
        await update_crawl_job_status(job_id, "completed")
        await update_crawl_job_stats(job_id, stats)
        
        logger.info(f"Crawl completed. Stats: {stats}")
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}")
        await update_crawl_job_status(job_id, "failed")
        await add_crawl_job_error(job_id, str(e))
        stats["errors"] += 1
        await update_crawl_job_stats(job_id, stats)
    
    finally:
        if driver:
            close_selenium_driver(driver)
