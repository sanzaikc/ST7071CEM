from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING, TEXT
from typing import Optional
from crawler.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Connect to MongoDB and create indexes"""
    logger.info(f"Connecting to MongoDB at {settings.mongodb_url}")
    try:
        mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
        mongodb.db = mongodb.client[settings.mongodb_db_name]
        
        # Test connection
        await mongodb.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close MongoDB connection"""
    if mongodb.client:
        logger.info("Closing MongoDB connection")
        mongodb.client.close()

async def create_indexes():
    """Create necessary indexes for collections"""
    logger.info("Creating database indexes...")
    
    # Publications collection indexes
    publications = mongodb.db.publications
    await publications.create_index("pure_id", unique=True)
    await publications.create_index("year")
    await publications.create_index("publication_type")
    await publications.create_index([("authors.pure_id", ASCENDING)])
    await publications.create_index([("title", TEXT), ("abstract", TEXT), ("keywords", TEXT)])
    await publications.create_index([("crawled_at", DESCENDING)])
    
    # Authors collection indexes
    authors = mongodb.db.authors
    await authors.create_index("pure_id", unique=True)
    await authors.create_index([("name", TEXT)])
    
    # Crawl jobs collection indexes
    crawl_jobs = mongodb.db.crawl_jobs
    await crawl_jobs.create_index([("started_at", DESCENDING)])
    await crawl_jobs.create_index("status")
    
    logger.info("Database indexes created successfully")

def get_database():
    """Get database instance"""
    return mongodb.db
