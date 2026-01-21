"""Functional approach to sitemap parsing - replaces sitemap_parser.py class"""
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from urllib.parse import urljoin
from utils.logger import setup_logger
from crawler.config import settings

logger = setup_logger(__name__)


def _is_sitemap_index(xml_content: str) -> bool:
    """Check if XML is a sitemap index"""
    return '<sitemapindex' in xml_content.lower()


def _parse_regular_sitemap(xml_content: str) -> List[Dict[str, any]]:
    """Parse a regular sitemap and return URLs"""
    urls = []
    
    try:
        root = ET.fromstring(xml_content)
        
        # Handle namespace
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # Find all URL entries
        for url_elem in root.findall('.//ns:url', namespace):
            url_data = {}
            
            loc_elem = url_elem.find('ns:loc', namespace)
            if loc_elem is not None and loc_elem.text:
                url_data['loc'] = loc_elem.text
            
            lastmod_elem = url_elem.find('ns:lastmod', namespace)
            if lastmod_elem is not None:
                url_data['lastmod'] = lastmod_elem.text
            
            priority_elem = url_elem.find('ns:priority', namespace)
            if priority_elem is not None:
                url_data['priority'] = float(priority_elem.text)
            
            if 'loc' in url_data:
                urls.append(url_data)
        
        logger.info(f"Parsed {len(urls)} URLs from sitemap")
        return urls
        
    except Exception as e:
        logger.error(f"Failed to parse sitemap XML: {e}")
        return []


def _parse_sitemap_index(base_url: str, xml_content: str, timeout: int) -> List[Dict[str, any]]:
    """Parse sitemap index and recursively parse child sitemaps"""
    logger.info("Detected sitemap index, parsing child sitemaps...")
    
    all_urls = []
    
    try:
        root = ET.fromstring(xml_content)
        
        # Handle namespace
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # Find all sitemap URLs
        for sitemap_elem in root.findall('.//ns:sitemap', namespace):
            loc_elem = sitemap_elem.find('ns:loc', namespace)
            if loc_elem is not None and loc_elem.text:
                child_sitemap_url = loc_elem.text
                logger.info(f"Parsing child sitemap: {child_sitemap_url}")
                
                # Recursively parse child sitemap
                child_urls = parse_sitemap(child_sitemap_url, timeout=timeout)
                all_urls.extend(child_urls)
        
        logger.info(f"Parsed {len(all_urls)} total URLs from sitemap index")
        return all_urls
        
    except Exception as e:
        logger.error(f"Failed to parse sitemap index: {e}")
        return []


def parse_sitemap(sitemap_url: str, timeout: int = 30) -> List[Dict[str, any]]:
    """Parse a sitemap and return list of URLs with metadata"""
    logger.info(f"Parsing sitemap: {sitemap_url}")
    
    try:
        response = requests.get(
            sitemap_url,
            timeout=timeout,
            headers={"User-Agent": settings.user_agent},
        )
        response.raise_for_status()
        
        # Check if it's a sitemap index or regular sitemap
        if _is_sitemap_index(response.text):
            return _parse_sitemap_index(sitemap_url, response.text, timeout)
        else:
            return _parse_regular_sitemap(response.text)
            
    except Exception as e:
        logger.error(f"Failed to parse sitemap {sitemap_url}: {e}")
        return []


def filter_urls_by_pattern(urls: List[Dict[str, any]], pattern: str) -> List[Dict[str, any]]:
    """Filter URLs by pattern"""
    filtered = [url for url in urls if pattern in url.get('loc', '')]
    logger.info(f"Filtered {len(filtered)} URLs matching pattern: {pattern}")
    return filtered


def extract_publication_urls(sitemap_url: str, timeout: int = 30) -> List[str]:
    """Extract publication URLs from sitemap"""
    urls = parse_sitemap(sitemap_url, timeout)
    pub_urls = filter_urls_by_pattern(urls, '/publications/')
    project_urls = filter_urls_by_pattern(urls, '/projects/')
    
    all_urls = [url['loc'] for url in pub_urls + project_urls]
    logger.info(f"Extracted {len(all_urls)} publication/project URLs")
    return all_urls
