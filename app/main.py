import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.documents import router as document_router
from app.api.knowledge_base import router as knowledge_base_router
from app.api.users import router as user_router
from app.core.config import settings
from app.core.middleware import RequestLoggingMiddleware
from app.db.session import dispose_database_engine
from app.services.document_worker import DocumentWorker


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    stop_worker = asyncio.Event()
    worker_task: asyncio.Task[None] | None = None
    if settings.DOCUMENT_WORKER_ENABLED:
        worker_task = asyncio.create_task(
            DocumentWorker().run_forever(stop_worker),
            name="document-worker",
        )
    try:
        yield
    finally:
        if worker_task is not None:
            stop_worker.set()
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass
        await dispose_database_engine()


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(knowledge_base_router)
app.include_router(document_router)