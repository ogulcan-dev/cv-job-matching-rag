# AI CV & Job Matching Backend (RAG + Vector Search)

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)
![pgvector](https://img.shields.io/badge/pgvector-0.3.0-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A production-ready backend service designed to intelligently match **Candidate CVs with Job Postings**.

The system uses **vector embeddings with PgVector** to perform semantic similarity search between CVs and job descriptions. It also includes a **Retrieval-Augmented Generation (RAG)** pipeline powered by OpenAI to explain *why* a candidate matches a job.

---

# Features

### CV Upload & Text Extraction
Accepts `.pdf`, `.docx`, and `.txt` CV files and extracts text for indexing.

### Job Posting Indexing
Stores job descriptions, company info, and tags in PostgreSQL.

### Semantic Vector Matching
Uses **OpenAI embeddings + pgvector cosine similarity** to match CVs with job descriptions based on meaning rather than exact keywords.

### Explainability (RAG Endpoint)
Uses OpenAI `gpt-4o-mini` to analyze the CV and job description and produce a structured explanation including:

- Match Score
- Strengths
- Skill Gaps
- Missing Keywords
- Recommended Learning Plan

### Production-Ready Architecture
- Async **SQLAlchemy 2.0**
- **Alembic** database migrations
- Dependency-injected API validation
- **Dockerized deployment**

---

# Tech Stack

**Backend**
- Python 3.11
- FastAPI
- Uvicorn

**Database**
- PostgreSQL
- pgvector (vector similarity search)

**AI / ML**
- OpenAI `text-embedding-3-small`
- OpenAI `gpt-4o-mini`

**ORM & Migrations**
- SQLAlchemy 2.0 (async)
- Alembic

**DevOps**
- Docker
- Docker Compose

---

# System Architecture

```
CV Upload
   │
   ▼
Text Extraction
   │
   ▼
OpenAI Embeddings
   │
   ▼
pgvector (PostgreSQL)
   │
   ▼
Cosine Similarity Search
   │
   ▼
Top Matching Jobs
   │
   ▼
RAG Explanation (OpenAI)
```

---

# Setup & Run (Docker)

## 1. Configure Environment Variables

```bash
cp .env.example .env
```

Add your OpenAI key:

```
OPENAI_API_KEY=your_key_here
```

---

## 2. Start Services

```bash
docker compose up --build
```

Detached mode:

```bash
docker compose up -d --build
```

---

## 3. Run Database Migrations

```bash
docker compose exec backend alembic upgrade head
```

---

# Local Development

## Create Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Mac/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Migrations

```bash
alembic upgrade head
```

## Start API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

# API Authentication

All endpoints require the header:

```
X-API-Key: dev-secret-key
```

---

# Example API Requests

## Upload CV

```bash
curl -X POST http://localhost:8000/cvs \
  -H "X-API-Key: dev-secret-key" \
  -F "file=@/path/to/cv.pdf"
```

---

## Create Job

```bash
curl -X POST http://localhost:8000/jobs \
  -H "X-API-Key: dev-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Backend Engineer",
    "company": "TechCorp",
    "description_text": "Python backend developer with FastAPI experience"
  }'
```

---

## Match CV → Jobs

```bash
curl -X POST http://localhost:8000/match/cv/<cv_id> \
  -H "X-API-Key: dev-secret-key"
```

---

## Explain Match (RAG)

```bash
curl -X POST http://localhost:8000/explain \
  -H "X-API-Key: dev-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"cv_id": "...", "job_id": "..."}'
```

---

# Testing

Run tests:

```bash
pytest
```

All tests mock the database and OpenAI API.

---

# License

MIT License
