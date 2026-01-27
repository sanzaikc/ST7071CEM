# Coventry Research Publications Search Engine

A vertical search engine specialized in retrieving papers and books published by members of Coventry University's Research Centre for Computational Science and Mathematical Modelling.

## Features

### Backend (FastAPI + MongoDB)

- **Polite Web Crawling**: Respects robots.txt and implements rate limiting
- **MongoDB Storage**: Persistent storage for publications and authors
- **Full-Text Search**: TF-IDF based search with cosine similarity ranking
- **Advanced Filtering**: Filter by year, author, and publication type
- **Scheduled Crawling**: Automatic updates on configurable schedule
- **RESTful API**: Complete API for search and data access
- **Background Tasks**: Non-blocking crawl operations

### Frontend (React + Vite + Tailwind CSS)

- **Modern UI**: Google Scholar-inspired search interface
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Search**: Instant results with relevance ranking
- **Publication Statistics**: View database metrics
- **Fast Performance**: Vite for lightning-fast development

## Architecture

```
Search Engine/
├── server/              # Backend (FastAPI)
│   ├── crawler/         # Web crawling components
│   ├── database/        # MongoDB connection and repositories
│   ├── indexing/        # Search engine logic
│   ├── models/          # Data models and schemas
│   ├── utils/           # Logging and utilities
│   └── main.py          # FastAPI application
└── ui/                  # Frontend (React)
    ├── src/
    │   ├── components/  # React components
    │   ├── services/    # API integration
    │   └── App.jsx      # Main application
    └── package.json
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB 6.0+

### Option 1: Start Everything (Windows)

```bash
start-all.bat
```

### Option 2: Start Everything (Linux/Mac)

```bash
./start-all.sh
```

### Option 3: Manual Start

**1. Start MongoDB**

```bash
mongod --dbpath C:\data\db  # Windows
mongod --dbpath /data/db    # Linux/Mac
```

**2. Start Backend**

```bash
cd server
python -m venv .venv
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # Linux/Mac
pip install -r requirements.txt
fastapi dev main.py
```

**3. Start Frontend**

```bash
cd ui
npm install
npm run dev
```

**4. Access the Application**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Setup Details

### Backend Setup

1. **Install Dependencies**

```bash
cd server
pip install -r requirements.txt
```

2. **Install and Start MongoDB**

Download and install MongoDB from https://www.mongodb.com/try/download/community

Start MongoDB:

```bash
# Windows
mongod --dbpath C:\data\db

# Linux/Mac
mongod --dbpath /data/db
```

3. **Configure Environment**

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

### Classification

- `POST /api/predict` - Classify text into Business, Entertainment, or Health

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

---

## Text Classification Module

### Overview

This project includes a **supervised text classification** system that categorizes documents into three predefined classes:

- **Business**: Financial news, market trends, corporate reports, economic updates
- **Entertainment**: Movies, music, celebrity news, arts, leisure activities
- **Health**: Medical articles, wellness tips, disease information, public health

### Why Classification Instead of Clustering?

| Aspect             | Clustering (Unsupervised) | Classification (Supervised)  |
| ------------------ | ------------------------- | ---------------------------- |
| **Labels**         | Inferred from data        | Explicitly provided          |
| **Training**       | Groups similar items      | Learns from labeled examples |
| **Accuracy**       | Variable, depends on data | Measurable, validated        |
| **Use Case**       | Discovery, exploration    | Prediction, assignment       |
| **Academic Rigor** | Less interpretable        | Clear evaluation metrics     |

For this assignment, **supervised classification** is preferred because:

1. We have predefined categories (Business, Entertainment, Health)
2. We need explicit, reproducible class assignments
3. We can measure and validate model performance
4. The workflow aligns with standard machine learning practices

### Classification Workflow

```
┌──────────────────────────────────────────────────────────────────┐
│                    SUPERVISED CLASSIFICATION                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. DATA COLLECTION                                               │
│     └─> 150 labeled documents (50 per category)                  │
│     └─> Sources: BBC News, Reuters, Medical journals             │
│     └─> Each doc has: text, label, source attribution            │
│                                                                   │
│  2. PREPROCESSING                                                 │
│     └─> Tokenization (split into words)                          │
│     └─> Stop-word removal (remove "the", "is", etc.)             │
│     └─> TF-IDF Vectorization (convert text to numbers)           │
│                                                                   │
│  3. MODEL TRAINING                                                │
│     └─> Algorithm: Multinomial Naive Bayes                       │
│     └─> Train/Validation split: 80%/20%                          │
│     └─> Learn word-to-category associations                      │
│                                                                   │
│  4. INFERENCE                                                     │
│     └─> User inputs new document                                 │
│     └─> Vectorize with same TF-IDF model                         │
│     └─> Predict class + confidence score                         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Using the Classification API

**Classify a Document:**

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "The stock market rallied today following positive earnings reports from tech companies."}'
```

**Response:**

```json
{
  "label": "Business",
  "confidence": 0.9234
}
```

### Dataset Information

The training dataset contains 150 documents:

- **50 Business** documents (financial news, market reports)
- **50 Entertainment** documents (movies, music, celebrities)
- **50 Health** documents (medical research, wellness)

Each document includes:

- `text`: Full sentence or paragraph content
- `label`: Category (Business/Entertainment/Health)
- `source`: Attribution to original source

**Note:** Documents are adapted from publicly available news sources for educational purposes. In production, include direct URLs and access dates.

### Technical Implementation

**Algorithm:** Multinomial Naive Bayes

- Optimal for text classification with word counts
- Based on Bayes' theorem: P(class|document) ∝ P(document|class) × P(class)
- Fast training and prediction
- Provides probability estimates

**Vectorization:** TF-IDF (Term Frequency - Inverse Document Frequency)

- Weights words by importance
- Reduces impact of common words
- Creates sparse numerical vectors

**Files:**

- `server/classification/model.py` - Classifier service
- `server/classification/data.py` - Labeled dataset
- `server/tests/test_classification_logic.py` - Unit tests

### Running Classification Tests

```bash
cd server
python -m tests.test_classification_logic
```

Expected output includes training accuracy, validation accuracy, and per-class feature importance.
