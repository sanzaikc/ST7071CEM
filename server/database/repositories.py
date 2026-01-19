"""Functional approach to database operations - replaces repositories.py"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from bson import ObjectId
from database.mongodb import get_database
from database.models import publication_doc, author_doc, crawl_job_doc
from utils.logger import setup_logger

logger = setup_logger(__name__)

# ============================================================================
# PUBLICATION OPERATIONS
# ============================================================================

async def create_publication(data: Dict[str, Any]) -> str:
    """Create new publication"""
    db = get_database()
    doc = publication_doc(data)
    result = await db.publications.insert_one(doc)
    logger.info(f"Created publication: {data['title']}")
    return str(result.inserted_id)


async def upsert_publication_by_pure_id(data: Dict[str, Any]) -> Tuple[str, bool]:
    """Update or insert publication by pure_id"""
    db = get_database()
    doc = publication_doc(data)
    result = await db.publications.update_one(
        {"pure_id": data["pure_id"]},
        {"$set": doc},
        upsert=True
    )
    is_new = result.upserted_id is not None
    doc_id = str(result.upserted_id) if is_new else await get_publication_id_by_pure_id(data["pure_id"])
    logger.info(f"{'Created' if is_new else 'Updated'} publication: {data['title']}")
    return doc_id, is_new


async def get_publication_id_by_pure_id(pure_id: str) -> Optional[str]:
    """Get MongoDB _id by pure_id"""
    db = get_database()
    doc = await db.publications.find_one({"pure_id": pure_id}, {"_id": 1})
    return str(doc["_id"]) if doc else None


async def find_publication_by_id(id: str) -> Optional[Dict[str, Any]]:
    """Find publication by MongoDB _id"""
    db = get_database()
    doc = await db.publications.find_one({"_id": ObjectId(id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def find_all_publications(skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
    """Find all publications with pagination"""
    db = get_database()
    cursor = db.publications.find().sort("crawled_at", -1).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def count_publications() -> int:
    """Count total publications"""
    db = get_database()
    return await db.publications.count_documents({})


async def search_publications(
    query: str, 
    filters: Dict[str, Any], 
    skip: int = 0, 
    limit: int = 10
) -> Tuple[List[Dict[str, Any]], int]:
    """Search publications with filters"""
    db = get_database()
    search_filter = {}
    
    # Text search
    if query:
        search_filter["$text"] = {"$search": query}
    
    # Year range filter
    if filters.get("year_from") or filters.get("year_to"):
        year_filter = {}
        if filters.get("year_from"):
            year_filter["$gte"] = filters["year_from"]
        if filters.get("year_to"):
            year_filter["$lte"] = filters["year_to"]
        search_filter["year"] = year_filter
    
    # Author filter
    if filters.get("author"):
        search_filter["authors.name"] = {"$regex": filters["author"], "$options": "i"}
    
    # Publication type filter
    if filters.get("publication_type"):
        search_filter["publication_type"] = filters["publication_type"]
    
    # Count total matching
    total = await db.publications.count_documents(search_filter)
    
    # Projection for text score
    projection = {"score": {"$meta": "textScore"}} if query else {}
    
    # Sort
    sort_key = [("score", {"$meta": "textScore"})] if query else [("year", -1)]
    if filters.get("sort") == "year_asc":
        sort_key = [("year", 1)]
    elif filters.get("sort") == "year_desc":
        sort_key = [("year", -1)]
    
    # Execute search
    cursor = db.publications.find(search_filter, projection).sort(sort_key).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    
    return results, total


async def get_publication_stats_by_year() -> Dict[int, int]:
    """Get publication count grouped by year"""
    db = get_database()
    pipeline = [
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    result = {}
    async for doc in db.publications.aggregate(pipeline):
        result[doc["_id"]] = doc["count"]
    return result


async def get_publication_stats_by_type() -> Dict[str, int]:
    """Get publication count grouped by type"""
    db = get_database()
    pipeline = [
        {"$group": {"_id": "$publication_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    result = {}
    async for doc in db.publications.aggregate(pipeline):
        result[doc["_id"]] = doc["count"]
    return result


# ============================================================================
# AUTHOR OPERATIONS
# ============================================================================

async def upsert_author_by_pure_id(data: Dict[str, Any]) -> Tuple[str, bool]:
    """Update or insert author by pure_id"""
    db = get_database()
    doc = author_doc(data)
    result = await db.authors.update_one(
        {"pure_id": data["pure_id"]},
        {"$set": doc},
        upsert=True
    )
    is_new = result.upserted_id is not None
    doc_id = str(result.upserted_id) if is_new else await get_author_id_by_pure_id(data["pure_id"])
    logger.info(f"{'Created' if is_new else 'Updated'} author: {data['name']}")
    return doc_id, is_new


async def get_author_id_by_pure_id(pure_id: str) -> Optional[str]:
    """Get MongoDB _id by pure_id"""
    db = get_database()
    doc = await db.authors.find_one({"pure_id": pure_id}, {"_id": 1})
    return str(doc["_id"]) if doc else None


async def find_author_by_id(id: str) -> Optional[Dict[str, Any]]:
    """Find author by MongoDB _id"""
    db = get_database()
    doc = await db.authors.find_one({"_id": ObjectId(id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def find_all_authors(skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
    """Find all authors with pagination"""
    db = get_database()
    cursor = db.authors.find().sort("name", 1).skip(skip).limit(limit)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def count_authors() -> int:
    """Count total authors"""
    db = get_database()
    return await db.authors.count_documents({})


async def increment_author_publication_count(pure_id: str):
    """Increment publication count for an author"""
    db = get_database()
    await db.authors.update_one(
        {"pure_id": pure_id},
        {"$inc": {"publication_count": 1}}
    )


# ============================================================================
# CRAWL JOB OPERATIONS
# ============================================================================

async def create_crawl_job(job_id: str, crawl_type: str) -> str:
    """Create new crawl job"""
    db = get_database()
    doc = crawl_job_doc(job_id, crawl_type)
    result = await db.crawl_jobs.insert_one(doc)
    logger.info(f"Created crawl job: {job_id}")
    return str(result.inserted_id)


async def update_crawl_job_status(job_id: str, status: str):
    """Update job status"""
    db = get_database()
    update_data = {"status": status, "updated_at": datetime.utcnow()}
    if status == "completed" or status == "failed":
        update_data["completed_at"] = datetime.utcnow()
    
    await db.crawl_jobs.update_one(
        {"job_id": job_id},
        {"$set": update_data}
    )


async def update_crawl_job_stats(job_id: str, stats: Dict[str, int]):
    """Update job statistics"""
    db = get_database()
    await db.crawl_jobs.update_one(
        {"job_id": job_id},
        {"$set": {"stats": stats}}
    )


async def add_crawl_job_error(job_id: str, error: str):
    """Add error to job log"""
    db = get_database()
    await db.crawl_jobs.update_one(
        {"job_id": job_id},
        {"$push": {"error_log": error}}
    )


async def find_crawl_job_by_id(job_id: str) -> Optional[Dict[str, Any]]:
    """Find job by job_id"""
    db = get_database()
    doc = await db.crawl_jobs.find_one({"job_id": job_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def find_latest_crawl_jobs(limit: int = 10) -> List[Dict[str, Any]]:
    """Find latest crawl jobs"""
    db = get_database()
    cursor = db.crawl_jobs.find().sort("started_at", -1).limit(limit)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def get_last_successful_crawl() -> Optional[datetime]:
    """Get timestamp of last successful crawl"""
    db = get_database()
    doc = await db.crawl_jobs.find_one(
        {"status": "completed"},
        sort=[("completed_at", -1)]
    )
    return doc["completed_at"] if doc else None
