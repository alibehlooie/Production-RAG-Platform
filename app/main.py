import asyncio
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import uvicorn
from app.core.config import settings
from collections.abc import AsyncIterator
from app.services.document_worker import DocumentWorker
from app.core.middleware import RequestLoggingMiddleware
from app.api.documents import router as document_router
from app.api.knowledge_base import router as knowledge_base_router
# @asynccontextmanager
# async def lifespan(_: FastAPI) -> AsyncIterator[None]:
#     stop_worker = asyncio.Event()
#     worker_task: asyncio.Task[None] | None = None
#     if settings.DOCUMENT_WORKER_ENABLED:
#         worker_task = asyncio.create_task(
#             DocumentWorker().run_forever(stop_worker),
#             name="document-worker",
#         )
#     try:
#         yield
#     finally:
#         if worker_task is not None:
#             stop_worker.set()
#             worker_task.cancel()
#             try:
#                 await worker_task
#             except asyncio.CancelledError:
#                 pass
#         # await close_vector_store()
#         # await close_lm_studio_client()
#         # await dispose_database_engine()

app = FastAPI(
    title = settings.APP_NAME,
    # lifespan = lifespan,
)

    
# app.add_middleware(RequestLoggingMiddleware)
# if settings.DEMO_MODE_ENABLED:
#     app.mount("/demo", StaticFiles(directory="app/web", html=True), name="demo")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(knowledge_base_router)
app.include_router(document_router)