"""Functional approach to crawl scheduling - replaces scheduler.py class"""
import uuid
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from crawler.config import settings
from crawler.pureportal import run_full_crawl
from database.repositories import create_crawl_job
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Global scheduler instance
_scheduler = None
_running = False


async def scheduled_crawl_task():
    """Task to run scheduled crawl"""
    logger.info("Running scheduled crawl task...")
    job_id = str(uuid.uuid4())
    
    try:
        # Create crawl job
        await create_crawl_job(job_id, "incremental")
        
        # Run crawler
        await run_full_crawl(job_id)
        
    except Exception as e:
        logger.error(f"Scheduled crawl failed: {e}")


def start_scheduler():
    """Start the scheduler"""
    global _scheduler, _running
    
    if _running:
        logger.warning("Scheduler already running")
        return
    
    if not settings.crawl_schedule_enabled:
        logger.info("Crawl scheduling is disabled")
        return
    
    logger.info("Starting crawl scheduler...")
    
    # Parse schedule time
    try:
        hour, minute = map(int, settings.crawl_schedule_time.split(':'))
    except:
        logger.error(f"Invalid schedule time format: {settings.crawl_schedule_time}")
        hour, minute = 2, 0
    
    # Create cron trigger based on interval
    if settings.crawl_schedule_interval == "daily":
        trigger = CronTrigger(hour=hour, minute=minute)
        logger.info(f"Scheduled daily crawl at {hour:02d}:{minute:02d}")
    elif settings.crawl_schedule_interval == "weekly":
        trigger = CronTrigger(day_of_week='mon', hour=hour, minute=minute)
        logger.info(f"Scheduled weekly crawl on Monday at {hour:02d}:{minute:02d}")
    elif settings.crawl_schedule_interval == "monthly":
        trigger = CronTrigger(day=1, hour=hour, minute=minute)
        logger.info(f"Scheduled monthly crawl on 1st at {hour:02d}:{minute:02d}")
    else:
        logger.error(f"Unknown schedule interval: {settings.crawl_schedule_interval}")
        return
    
    # Create and configure scheduler
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        scheduled_crawl_task,
        trigger=trigger,
        id='scheduled_crawl',
        replace_existing=True
    )
    
    _scheduler.start()
    _running = True
    logger.info("Crawl scheduler started")


def stop_scheduler():
    """Stop the scheduler"""
    global _scheduler, _running
    
    if _scheduler and _scheduler.running:
        logger.info("Stopping crawl scheduler...")
        _scheduler.shutdown()
        _running = False
        logger.info("Crawl scheduler stopped")
