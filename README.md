# AI CV & Job Matching Backend

A production-ready backend service to upload CVs, index Jobs, and perform hybrid searches (Vector Similarity + Keyword Full-Text Search) to match candidates and jobs.

## Tech Stack
- Python 3.11, FastAPI
- PostgreSQL + pgvector (asyncpg)
- SQLAlchemy + Alembic
- OpenAI (Embeddings + Chat/RAG)

## Setup & Run (Docker)

To run the application entirely in Docker (which includes the Postgres `pgvector` database and the FastAPI backend):

1. **Configure Environment variables**
   Copy `.env.example` to `.env` and insert your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and set OPENAI_API_KEY
   ```

2. **Start Services**
   Run the following command to build and start the containers. You can run it attached to see the logs, or detached.
   
   To see the logs and run attached:
   ```bash
   docker compose up --build
   ```

   Or to run in the background (detached mode):
   ```bash
   docker compose up -d --build
   ```

   Wait a few seconds for Postgres to become healthy.

3. **Run Database Migrations**
   Initialize the database schema with pgvector extensions and full-text search triggers:
   ```bash
   docker compose exec backend alembic upgrade head
   ```

## Setup & Run (Local / Without Docker)

To run the application locally on your machine, you still need a Postgres database with the `pgvector` extension installed.

1. **Configure Environment variables**
   Copy `.env.example` to `.env` and configure your `OPENAI_API_KEY` and your local `DATABASE_URL`.
   ```bash
   cp .env.example .env
   ```

2. **Install Python Dependencies**
   Create a virtual environment and install the required packages:

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
   Make sure your local Postgres is running, then apply migrations:
   ```bash
   alembic upgrade head
   ```

4. **Start the FastAPI Server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Example cURL Commands

**Note:** All endpoints use the `X-API-Key` header for authentication. By default, it's `dev-secret-key`.

### 1. Upload CV
Requires a `multipart/form-data` payload containing the file (PDF, DOCX, TXT):
```bash
curl -X POST http://localhost:8000/cvs \
  -H "X-API-Key: dev-secret-key" \
  -F "file=@/path/to/your/cv.pdf" \
  -F "candidate_name=John Doe" \
  -F "title=Backend Engineer"
```

### 2. Create Job Posting
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

### 3. Match CV -> Jobs
```bash
curl -X POST http://localhost:8000/match/cv/<cv_id_here> \
  -H "X-API-Key: dev-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"top_k": 5}'
```

### 4. Explain Match (RAG)
```bash
curl -X POST http://localhost:8000/explain \
  -H "X-API-Key: dev-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"cv_id": "<cv_id_here>", "job_id": "<job_id_here>"}'
```

## Running Tests Locally
To run the Pytest suite (mocks external APIs and DB):
```bash
pip pytest
pytest
```
