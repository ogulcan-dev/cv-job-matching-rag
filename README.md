# AI CV & Job Matching Backend (RAG + Hybrid Search)

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)
![pgvector](https://img.shields.io/badge/pgvector-0.3.0-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A production-ready backend service designed to intelligently match Candidate CVs with Job Postings. 
It leverages **Hybrid Search**—combining PgVector's semantic cosine similarity and PostgreSQL's native Full-Text Keyword Search—along with a Retrieval-Augmented Generation (RAG) architecture powered by OpenAI to explain *why* a candidate matches a job.

## Features

- **CV Upload & Text Extraction**: Accepts `.pdf`, `.docx`, and `.txt` files.
- **Job Posting Indexing**: Stores rich text descriptions and tags.
- **Hybrid Search Engine**: Matches CVs to Jobs (and Jobs to CVs) using a weighted formula:
  `Final Score = (0.75 * Vector Similarity) + (0.25 * Keyword TS_Rank)`
- **Explainability (RAG Endpoint)**: Queries OpenAI `gpt-4o-mini` with the relevant context chunks to return a strict JSON evaluation featuring: Match Score, Strengths, Gaps, Missing Keywords, and a Recommended Learning Plan.
- **Production-minded Stack**: Asynchronous SQLAlchemy 2.0, Alembic migrations, dependency-injected API validation, and Docker out-of-the-box.

## Tech Stack
- **Framework:** Python 3.11, FastAPI, Uvicorn
- **Database:** PostgreSQL with `pgvector`
- **ORM & Migrations:** SQLAlchemy 2.0 (asyncpg), Alembic
- **AI/LLM:** OpenAI Models (`text-embedding-3-small` / `gpt-4o-mini`)
- **Containerization:** Docker, Docker Compose

---

## 🚀 Setup & Run (Docker - Recommended)

To run the application entirely in Docker (which automatically provisions the Postgres `pgvector` database and the FastAPI backend):

1. **Configure Environment variables**
   Copy `.env.example` to `.env` and insert your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and set OPENAI_API_KEY
   ```

2. **Start Services**
   Run the following command to build and start the containers.
   
   To see the logs (attached mode):
   ```bash
   docker compose up --build
   ```

   To run in the background (detached mode):
   ```bash
   docker compose up -d --build
   ```

3. **Run Database Migrations**
   Initialize the database schema with pgvector extensions and full-text search triggers:
   ```bash
   docker compose exec backend alembic upgrade head
   ```

---

## 💻 Setup & Run (Local / Without Docker)

To run the application locally on your machine, you must have a local Postgres database with the `pgvector` extension installed.

1. **Configure Environment variables**
   Copy `.env.example` to `.env` and configure your `OPENAI_API_KEY` and your local `DATABASE_URL`.

2. **Install Python Dependencies**
   
   **For Windows:**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

   **For macOS/Linux:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run Database Migrations**
   Ensure your local Postgres is running, then apply migrations:
   ```bash
   alembic upgrade head
   ```

4. **Start the FastAPI Server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## 🧰 API Usage & Postman

All endpoints use API Key Authentication via headers. By default, the required header is:
`X-API-Key: dev-secret-key`

To make testing easier, a ready-to-use **Postman Collection** is included in the root directory: `postman_collection.json`. Simply import this file into Postman, and you will have pre-configured endpoints for uploading CVs, creating jobs, matching, and executing RAG.

### Example cURL Commands

**1. Upload CV** *(multipart/form-data)*
```bash
curl -X POST http://localhost:8000/cvs \
  -H "X-API-Key: dev-secret-key" \
  -F "file=@/path/to/your/cv.pdf" \
  -F "candidate_name=John Doe" \
  -F "title=Backend Engineer"
```

**2. Create Job Posting**
```bash
curl -X POST http://localhost:8000/jobs \
  -H "X-API-Key: dev-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Backend Engineer",
    "company": "TechCorp",
    "location": "Remote",
    "description_text": "Looking for a seasoned Python backend engineer familiar with FastAPI, PostgreSQL and pgvector.",
    "tags": ["python", "fastapi", "postgres"]
  }'
```

**3. Match CV -> Jobs**
```bash
curl -X POST http://localhost:8000/match/cv/<cv_id_here> \
  -H "X-API-Key: dev-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"top_k": 5}'
```

**4. Explain Match (RAG)**
```bash
curl -X POST http://localhost:8000/explain \
  -H "X-API-Key: dev-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"cv_id": "<cv_id_here>", "job_id": "<job_id_here>"}'
```

---

## 🧪 Testing

The repository uses `pytest`. It includes fully mocked tests for the database and the OpenAI API, meaning you can test the logic without spending API credits or needing a live database.

```bash
pytest
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
