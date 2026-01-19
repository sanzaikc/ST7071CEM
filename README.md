# Coventry Research Publications Search Engine

A vertical search engine specialized in retrieving papers and books published by members of Coventry University's Research Centre for Computational Science and Mathematical Modelling.

## Features

- **Polite Web Crawling**: Respects robots.txt and implements rate limiting
- **MongoDB Storage**: Persistent storage for publications and authors
- **Full-Text Search**: Search across titles, abstracts, and keywords
- **Advanced Filtering**: Filter by year, author, and publication type
- **Scheduled Crawling**: Automatic updates on configurable schedule
- **RESTful API**: Complete API for search and data access
- **Background Tasks**: Non-blocking crawl operations

## Architecture

```
server/
├── crawler/          # Web crawling components
├── database/         # MongoDB connection and repositories
├── indexing/         # Search engine logic
├── models/           # Data models and schemas
├── utils/            # Logging and utilities
└── main.py          # FastAPI application
```

## Setup

### 1. Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

### 2. Install and Start MongoDB

Download and install MongoDB from https://www.mongodb.com/try/download/community

Start MongoDB:

```bash
# Windows
mongod --dbpath C:\data\db

# Linux/Mac
mongod --dbpath /data/db
```

### 3. Configure Environment

Edit `.env` file in the project root:

```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=coventry_research
CRAWL_DELAY=2.5
CRAWL_SCHEDULE_ENABLED=true
CRAWL_SCHEDULE_INTERVAL=daily
CRAWL_SCHEDULE_TIME=02:00
```

### 4. Run the Application

```bash
# If not already in server directory
cd server
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

## Usage

### Initial Crawl

Trigger the first crawl to populate the database:

```bash
curl -X POST http://localhost:8000/api/crawl/trigger \
  -H "Content-Type: application/json" \
  -d '{"crawl_type": "full"}'
```

This returns a job_id. Check the status:

```bash
curl http://localhost:8000/api/crawl/status/{job_id}
```

### Search Publications

```bash
# Basic search
curl "http://localhost:8000/api/search?q=machine+learning&page=1&limit=10"

# Search with filters
curl "http://localhost:8000/api/search?q=neural+networks&year_from=2020&year_to=2024&publication_type=journal_article"

# Search by author
curl "http://localhost:8000/api/search?q=&author=Smith&sort=year_desc"
```

### Get Publications

```bash
# List all publications
curl "http://localhost:8000/api/publications?page=1&limit=10"

# Get specific publication
curl "http://localhost:8000/api/publications/{publication_id}"
```

### Get Authors

```bash
# List all authors
curl "http://localhost:8000/api/authors?page=1&limit=50"

# Get specific author
curl "http://localhost:8000/api/authors/{author_id}"

# Get author's publications
curl "http://localhost:8000/api/authors/{author_id}/publications"
```

### Get Statistics

```bash
curl "http://localhost:8000/api/stats"
```

## API Endpoints

### Crawling

- `POST /api/crawl/trigger` - Trigger on-demand crawl
- `GET /api/crawl/status/{job_id}` - Get crawl job status
- `GET /api/crawl/jobs` - List recent crawl jobs

### Search

- `GET /api/search` - Search publications with filters

### Publications

- `GET /api/publications` - List all publications
- `GET /api/publications/{id}` - Get publication details
- `GET /api/publications/stats` - Get statistics

### Authors

- `GET /api/authors` - List all authors
- `GET /api/authors/{id}` - Get author details
- `GET /api/authors/{id}/publications` - Get author's publications

### System

- `GET /api/health` - Health check
- `GET /api/stats` - Overall statistics
- `GET /` - API information

## Crawler Behavior

### Politeness

- Respects `robots.txt` rules
- Configurable delay between requests (default: 2.5 seconds)
- Headless browser to avoid detection
- Proper user-agent identification

### Scheduling

- Automatic crawls run based on configured schedule
- Default: Daily at 2:00 AM
- Can be disabled via `.env` configuration
- Incremental updates to avoid re-crawling all data

### Data Extraction

For each publication, the crawler extracts:

- Title
- Authors (with profile links)
- Publication year
- Publication type
- Abstract
- Keywords
- DOI (if available)
- External links

## MongoDB Collections

### publications

Stores publication metadata with indexes on:

- `pure_id` (unique)
- `year`, `publication_type`, `authors.pure_id`
- Text index on title, abstract, keywords

### authors

Stores author information with indexes on:

- `pure_id` (unique)
- `name` (text index)

### crawl_jobs

Tracks crawl operations and statistics

## Development

### Running Tests

```bash
pytest
```

### Viewing Logs

Logs are output to console. To save to file, modify the logger configuration in `utils/logger.py`.

### Adding New Features

1. Add data models in `models/schemas.py`
2. Update database repositories in `database/repositories.py`
3. Implement business logic in appropriate modules
4. Add API endpoints in `main.py`

## Troubleshooting

### MongoDB Connection Issues

- Ensure MongoDB is running
- Check `MONGODB_URL` in `.env`
- Verify firewall settings

### Crawling Errors

- Check robots.txt permissions
- Verify target URL is accessible
- Increase `CRAWL_DELAY` if getting rate limited
- Check crawler logs for specific errors

### Search Not Working

- Ensure MongoDB text indexes are created
- Run initial crawl to populate database
- Check query syntax in API docs

## License

Educational project for STW7071CEM Information Retrieval course.
