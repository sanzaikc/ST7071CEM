import asyncio
import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, WebSocket
from starlette.websockets import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.mongodb import connect_to_mongo, close_mongo_connection
from database.repositories import (
    create_crawl_job,
    find_crawl_job_by_id,
    find_latest_crawl_jobs,
    get_last_successful_crawl
)
from crawler.pureportal import run_full_crawl
from crawler.events import hub
from crawler.scheduler import start_scheduler, stop_scheduler
from indexing.search_engine import (
    search,
    get_publication_by_id,
    get_all_publications,
    get_publications_by_author,
    get_statistics,
    get_author_by_id,
    get_all_authors
)
from models.schemas import (
    SearchQuery, SearchResponse, PublicationResponse,
    AuthorResponse, CrawlJobCreate, CrawlJobResponse,
    StatsResponse, PublicationType, ClusterRequest, ClusterResponse
)
from utils.logger import setup_logger
from clustering.model import cluster_service

logger = setup_logger(__name__)

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    await connect_to_mongo()

    # Initialize clustering model
    logger.info("Training clustering model...")
    try:
        cluster_service.train()
        logger.info("Clustering model trained.")
    except Exception as e:
        logger.error(f"Failed to train clustering model: {e}")

    start_scheduler()
    yield
    # Shutdown

    logger.info("Shutting down application...")
    stop_scheduler()
    await close_mongo_connection()

app = FastAPI(
    title="Coventry Research Publications Search Engine",
    description="A vertical search engine for Coventry University Research Centre publications",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Coventry Research Publications Search Engine API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search",
            "publications": "/api/publications",
            "authors": "/api/authors",
            "crawl": "/api/crawl/trigger",
            "predict": "/api/predict",
            "docs": "/docs"
        }
    }


# Health check
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "clustering": "trained" if cluster_service.is_trained else "not trained"
    }


# Clustering endpoint
@app.post("/api/predict", response_model=ClusterResponse)
async def predict_category(request: ClusterRequest):
    """Predict the category of the given text"""
    category = cluster_service.predict(request.text)
    return ClusterResponse(category=category)


# Crawl endpoints
@app.post("/api/crawl/trigger", response_model=CrawlJobResponse)
async def trigger_crawl(
    background_tasks: BackgroundTasks,
    crawl_job: Optional[CrawlJobCreate] = None
):
    """Trigger on-demand crawl"""
    crawl_type = crawl_job.crawl_type if crawl_job else "full"
    logger.info(f"Triggering {crawl_type} crawl...")
    
    job_id = str(uuid.uuid4())
    
    # Create job record
    await create_crawl_job(job_id, crawl_type)
    
    # Run crawl in background
    background_tasks.add_task(run_full_crawl, job_id)
    
    # Return job info
    job = await find_crawl_job_by_id(job_id)
    return job


@app.get("/api/crawl/status/{job_id}", response_model=CrawlJobResponse)
async def get_crawl_status(job_id: str):
    """Get crawl job status"""
    job = await find_crawl_job_by_id(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@app.get("/api/crawl/jobs", response_model=List[CrawlJobResponse])
async def get_crawl_jobs(limit: int = 10):
    """Get recent crawl jobs"""
    jobs = await find_latest_crawl_jobs(limit=limit)
    return jobs


# Search endpoint
@app.get("/api/search", response_model=SearchResponse)
async def search_publications(
    q: str = Query(..., description="Search query"),
    year_from: Optional[int] = Query(None, description="Filter from year"),
    year_to: Optional[int] = Query(None, description="Filter to year"),
    author: Optional[str] = Query(None, description="Filter by author name"),
    publication_type: Optional[PublicationType] = Query(None, description="Filter by publication type"),
    sort: str = Query("relevance", description="Sort by: relevance, year_desc, year_asc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Results per page")
):
    """Search publications"""
    search_query = SearchQuery(
        q=q,
        year_from=year_from,
        year_to=year_to,
        author=author,
        publication_type=publication_type,
        sort=sort,
        page=page,
        limit=limit
    )
    
    results, total = await search(search_query)
    
    return SearchResponse(
        total=total,
        page=page,
        limit=limit,
        results=results
    )


# Publication endpoints
@app.get("/api/publications", response_model=SearchResponse)
async def get_publications(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """Get all publications"""
    results, total = await get_all_publications(page=page, limit=limit)
    
    return SearchResponse(
        total=total,
        page=page,
        limit=limit,
        results=results
    )


@app.get("/api/publications/{publication_id}", response_model=PublicationResponse)
async def get_publication(publication_id: str):
    """Get publication by ID"""
    publication = await get_publication_by_id(publication_id)
    
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    return publication


# Author endpoints
@app.get("/api/authors")
async def get_authors(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    """Get all authors"""
    results, total = await get_all_authors(page=page, limit=limit)
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "results": results
    }


@app.get("/api/authors/{author_id}", response_model=AuthorResponse)
async def get_author(author_id: str):
    """Get author by ID"""
    author = await get_author_by_id(author_id)
    
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    return author


@app.get("/api/authors/{author_id}/publications", response_model=SearchResponse)
async def get_author_publications(
    author_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """Get publications by author"""
    # First get the author to get their pure_id
    author = await get_author_by_id(author_id)
    
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    results, total = await get_publications_by_author(
        author["pure_id"],
        page=page,
        limit=limit
    )
    
    return SearchResponse(
        total=total,
        page=page,
        limit=limit,
        results=results
    )


# Statistics endpoint
@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get overall statistics"""
    stats = await get_statistics()
    last_crawl = await get_last_successful_crawl()
    
    return StatsResponse(
        total_publications=stats["total_publications"],
        total_authors=stats["total_authors"],
        publications_by_year=stats["publications_by_year"],
        publications_by_type=stats["publications_by_type"],
        last_crawl=last_crawl
    )


@app.websocket("/ws/crawl/{job_id}")
async def crawl_events_ws(websocket: WebSocket, job_id: str):
    await websocket.accept()
    await hub.subscribe(job_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await hub.unsubscribe(job_id, websocket)
