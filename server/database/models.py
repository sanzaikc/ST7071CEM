from datetime import datetime
from typing import Dict, Any

def publication_doc(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create publication document for MongoDB"""
    now = datetime.utcnow()
    return {
        "pure_id": data["pure_id"],
        "title": data["title"],
        "authors": data["authors"],
        "year": data["year"],
        "publication_type": data["publication_type"],
        "abstract": data.get("abstract"),
        "keywords": data.get("keywords", []),
        "publication_url": data["publication_url"],
        "doi": data.get("doi"),
        "external_url": data.get("external_url"),
        "crawled_at": now,
        "updated_at": now
    }

def author_doc(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create author document for MongoDB"""
    now = datetime.utcnow()
    return {
        "pure_id": data["pure_id"],
        "name": data["name"],
        "profile_url": data["profile_url"],
        "department": data.get("department"),
        "email": data.get("email"),
        "publication_count": 0,
        "crawled_at": now,
        "updated_at": now
    }

def crawl_job_doc(job_id: str, crawl_type: str) -> Dict[str, Any]:
    """Create crawl job document for MongoDB"""
    return {
        "job_id": job_id,
        "status": "pending",
        "crawl_type": crawl_type,
        "started_at": datetime.utcnow(),
        "completed_at": None,
        "stats": {
            "authors_crawled": 0,
            "publications_found": 0,
            "new_publications": 0,
            "updated_publications": 0,
            "errors": 0
        },
        "error_log": []
    }
