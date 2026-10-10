# Build Guide: Creating a Project Like AI RAG Platform

A step-by-step order for building a multi-user RAG backend from scratch. The order follows this repo's own history (migrations `0001`–`0006` and `CHANGELOG.md`). Each phase ends with something runnable.

## Phase 0: Setup (~0.5 day)
- [ ] Create the repo: `pyproject.toml`, `requirements.txt`, `.gitignore`, `.env.example`
- [ ] `app/core/config.py` using Pydantic Settings
- [ ] `app/main.py` with `GET /health`
- [ ] First test (`tests/test_health.py`)
- [ ] `Makefile` with `lint`, `test`, `run`

## Phase 1: Data foundation
- [ ] PostgreSQL in `docker-compose.yml`
- [ ] `db/session.py`, `db/base.py` (SQLAlchemy)
- [ ] Alembic setup and migration `0001` (initial schema)
- [ ] Models: `KnowledgeBase`, `Document`, `DocumentChunk`
- [ ] Pydantic `schemas/`
- [ ] Thin `api/` routes that call `services/`

Keep the layering: `api/` -> `services/` -> `db/`, `rag/`, `llm/`. Routes hold no business logic.

## Phase 2: Ingestion pipeline
- [ ] Upload endpoint with file type and size validation
- [ ] `services/text_extraction.py` (PDF, TXT)
- [ ] `services/chunking.py` (chunks with overlap) and unit tests
- [ ] `llm/client.py` with `embed_texts` (LM Studio, Ollama or OpenAI)
- [ ] Qdrant in compose and `rag/vector_store.py` (one vector per chunk)

## Phase 3: Retrieval and QA
- [ ] `services/search.py`: embed the query, then search Qdrant
- [ ] `POST /search`
- [ ] `services/qa.py`: retrieve, build the prompt, call the LLM, return the answer and sources
- [ ] `POST /qa/ask`
- [ ] Anti-hallucination prompt guard ("I don't know" when the context is insufficient)

**Milestone:** a working end-to-end RAG demo. Aim for this within about a week.

## Phase 4: Multi-user and security
- [ ] `User` model and migration `0002`
- [ ] `user_id` ownership on every resource
- [ ] JWT auth, then register/login with bcrypt (migration `0006`)
- [ ] `tests/test_tenant_isolation.py`: user A cannot access user B's data

## Phase 5: Conversation memory
- [ ] `Conversation` and `Message` models (migration `0003`)
- [ ] Include recent history in the QA prompt
- [ ] `GET /conversations`

## Phase 6: Async processing
- [ ] `DocumentJob` model and status fields (migrations `0004`, `0005`)
- [ ] Upload returns immediately with a `pending` job
- [ ] `worker.py` and `services/document_worker.py` as a separate compose service
- [ ] Failure handling, retries, `POST /documents/{id}/reindex`

## Phase 7: Retrieval quality
- [ ] Hybrid search: vector search plus Postgres full-text search
- [ ] Reciprocal Rank Fusion (`rag/fusion.py`)
- [ ] Reranker (`rag/reranker.py`)
- [ ] SSE streaming on `/qa/ask/stream` (sources first, then tokens)

## Phase 8: Production quality
- [ ] Structured JSON logging and request-ID middleware
- [ ] `/metrics` endpoint (Prometheus)
- [ ] Readiness checks for DB, Qdrant and LLM
- [ ] Multi-stage `Dockerfile` with a non-root user
- [ ] GitHub Actions CI with Postgres and Qdrant service containers
- [ ] Delete cascades across Postgres, Qdrant and disk

## Phase 9: Evaluation, UI, docs
- [ ] `evaluation/run_eval.py`, a question set, and an LLM-as-judge mode
- [ ] Simple static UI in `app/web`
- [ ] README, `ARCHITECTURE.md`, screenshots, API examples
- [ ] Written trade-offs to use as interview talking points

## Priorities for interview prep
| Priority | Phases |
|---|---|
| Must have | 0–4, 6, 8 |
| Strong extras | 5, 7 |
| Optional polish | 9 (UI, cloud docs) |

## Tips
- Get a working end-to-end flow (Phases 0–3) before adding anything else.
- Write tests as you go, especially for chunking, fusion and tenant isolation.
- Write each piece yourself and be ready to explain why. Typical questions:
  - Why chunk overlap?
  - Why RRF?
  - How do you prevent cross-tenant leaks?
  - Why a background worker?
  - How do you evaluate answer quality?

