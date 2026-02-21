# Enterprise AI Assistant

AI-powered assistant that answers internal company questions using Retrieval-Augmented Generation (RAG). Upload documents, and the system chunks, embeds, and indexes them in a vector database — then answers natural-language questions grounded in your knowledge base.

## Architecture

```
                         ┌────────────────────────┐
                         │    Frontend Chat UI     │
                         │   (served at /ui/)      │
                         └───────────┬────────────┘
                                     │  HTTP
                         ┌───────────▼────────────┐
                         │    FastAPI Backend      │
                         │                        │
                         │  /query/   /documents/ │
                         │  /health/              │
                         └──┬──────────┬──────────┘
                            │          │
              ┌─────────────▼──┐  ┌────▼──────────────┐
              │   PostgreSQL   │  │  Google Gemini API │
              │   + pgvector   │  │  (LLM generation)  │
              │                │  └───────────────────┘
              │  documents     │
              │  chunks +      │  ┌───────────────────┐
              │  embeddings    │  │ Sentence           │
              │  query_logs    │  │ Transformers       │
              └────────────────┘  │ (all-MiniLM-L6-v2) │
                                  └───────────────────┘
```

**RAG Pipeline:** Question → Embed → pgvector similarity search → Top-k chunks → Gemini generates answer grounded in context

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI |
| Database | PostgreSQL 16 + pgvector |
| LLM | Google Gemini 2.0 Flash |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2, 384-dim) |
| Frontend | Vanilla HTML/CSS/JS (served by FastAPI) |
| Infrastructure | Docker, docker-compose, GitHub Actions CI |

## Quick Start

### Option A: Docker (recommended)

```bash
# 1. Clone and configure
git clone <your-repo-url>
cd enterprise-ai-assistant
cp .env.example .env
# Edit .env — set your GEMINI_API_KEY

# 2. Run
docker-compose up --build

# 3. Open
# Chat UI:  http://localhost:8000/ui/
# API docs: http://localhost:8000/docs
```

### Option B: Local development

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up PostgreSQL with pgvector
# Create a database called enterprise_assistant
# Make sure the pgvector extension is installed

# 4. Configure environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY and DATABASE_URL

# 5. Run
uvicorn app.main:app --reload --port 8000

# 6. Open
# Chat UI:  http://localhost:8000/ui/
# API docs: http://localhost:8000/docs
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Welcome message |
| `GET` | `/health/` | App health check |
| `GET` | `/health/db` | Database connectivity check |
| `POST` | `/documents/upload` | Upload and process a PDF or TXT file |
| `GET` | `/documents/` | List all uploaded documents |
| `DELETE` | `/documents/{id}` | Delete a document and its chunks |
| `POST` | `/query/` | Ask a question (RAG pipeline) |
| `GET` | `/query/history` | View recent queries |
| `GET` | `/query/{id}` | Get a specific query log entry |

## Project Structure

```
app/
├── main.py                 # FastAPI app entry point, router registration
├── config.py               # Environment config (Pydantic settings)
├── database.py             # SQLAlchemy engine, session, Base
├── models/
│   ├── document.py         # Document + DocumentChunk (with pgvector embedding)
│   └── query_log.py        # QueryLog (stores questions + answers)
├── schemas/
│   └── query.py            # Pydantic DTOs (QueryRequest, QueryResponse, etc.)
├── services/
│   ├── embedding_service.py    # Sentence Transformers embedding generation
│   ├── gemini_service.py       # Google Gemini LLM wrapper
│   ├── document_service.py     # Document ingestion pipeline
│   ├── retrieval_service.py    # pgvector cosine similarity search
│   └── query_service.py        # RAG orchestrator (embed → retrieve → generate → log)
├── routes/
│   ├── health.py           # Health check endpoints
│   ├── documents.py        # Document upload/list/delete
│   └── query.py            # Query endpoints
├── utils/
│   └── text_processing.py  # PDF/text extraction, chunking
└── static/
    └── index.html          # Frontend chat UI
```
