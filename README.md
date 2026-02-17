# Enterprise AI Assistant

AI-powered assistant that answers internal company questions using Retrieval-Augmented Generation (RAG).

## Tech Stack
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL + pgvector
- **LLM:** Google Gemini
- **Embeddings:** Sentence Transformers

## Quick Start

### 1. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up PostgreSQL
Create a database called `enterprise_assistant`:
```sql
CREATE DATABASE enterprise_assistant;
```

### 4. Configure environment
Edit `.env` with your actual values:
- `GEMINI_API_KEY` — get from https://aistudio.google.com/app/apikey
- `DATABASE_URL` — update password to match your PostgreSQL setup

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

### 6. Test it
- Open http://localhost:8000 — should see welcome message
- Open http://localhost:8000/docs — interactive API docs
- Open http://localhost:8000/health/ — health check
- Open http://localhost:8000/health/db — database connection check
