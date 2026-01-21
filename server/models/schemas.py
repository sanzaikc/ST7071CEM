from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class PublicationType(str, Enum):
    JOURNAL_ARTICLE = "journal_article"
    CONFERENCE_PAPER = "conference_paper"
    BOOK = "book"
    BOOK_CHAPTER = "book_chapter"
    THESIS = "thesis"
    REPORT = "report"
    OTHER = "other"

class CrawlType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    ON_DEMAND = "on_demand"

class CrawlStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# API Request/Response Models

class AuthorBase(BaseModel):
    name: str
    profile_url: str
    pure_id: str

class AuthorCreate(AuthorBase):
    department: Optional[str] = None
    email: Optional[str] = None

class AuthorResponse(AuthorBase):
    id: str = Field(alias="_id")
    department: Optional[str] = None
    email: Optional[str] = None
    publication_count: int = 0
    crawled_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class PublicationAuthor(BaseModel):
    name: str
    profile_url: str
    pure_id: str

class PublicationBase(BaseModel):
    title: str
    authors: List[PublicationAuthor]
    year: int
    publication_type: PublicationType
    abstract: Optional[str] = None
    keywords: List[str] = []
    publication_url: str

class PublicationCreate(PublicationBase):
    pure_id: str
    doi: Optional[str] = None
    external_url: Optional[str] = None

class PublicationResponse(PublicationBase):
    id: str = Field(alias="_id")
    pure_id: str
    doi: Optional[str] = None
    external_url: Optional[str] = None
    score: Optional[float] = None
    cosine_similarity: Optional[float] = None
    crawled_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class SearchQuery(BaseModel):
    q: str
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    author: Optional[str] = None
    publication_type: Optional[PublicationType] = None
    sort: str = "relevance"
    page: int = 1
    limit: int = 10

class SearchResponse(BaseModel):
    total: int
    page: int
    limit: int
    results: List[PublicationResponse]

class CrawlJobStats(BaseModel):
    authors_crawled: int = 0
    publications_found: int = 0
    new_publications: int = 0
    updated_publications: int = 0
    errors: int = 0

class ClusterRequest(BaseModel):
    text: str

class ClusterResponse(BaseModel):
    category: str
    cluster_id: Optional[int] = None

class CrawlJobCreate(BaseModel):
    crawl_type: CrawlType = CrawlType.FULL
    
class CrawlJobResponse(BaseModel):
    id: str = Field(alias="_id")
    job_id: str
    status: CrawlStatus
    crawl_type: CrawlType
    started_at: datetime
    completed_at: Optional[datetime] = None
    stats: CrawlJobStats
    error_log: List[str] = []
    
    class Config:
        populate_by_name = True

class StatsResponse(BaseModel):
    total_publications: int
    total_authors: int
    publications_by_year: dict
    publications_by_type: dict
    last_crawl: Optional[datetime] = None
