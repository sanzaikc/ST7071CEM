from pathlib import Path

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "coventry_research"
    
    # Crawler
    crawl_delay: float = 2.5
    crawl_timeout: int = 30
    max_retries: int = 3
    respect_robots_txt: bool = False
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    target_url: str = "https://pureportal.coventry.ac.uk/en/organisations/ics-research-centre-for-computational-science-and-mathematical-mo/publications/"
    
    # Scheduler
    crawl_schedule_enabled: bool = True
    crawl_schedule_interval: str = "daily"
    crawl_schedule_time: str = "02:00"
    
    # API   
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        # Prefer workspace-root .env, but also allow server/.env overrides.
        _root_dir = Path(__file__).resolve().parents[2]
        env_file = (
            str(_root_dir / ".env"),
            ".env",
        )
        case_sensitive = False

settings = Settings()
