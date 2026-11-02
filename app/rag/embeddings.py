from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings


class EmbeddingError(RuntimeError):
    """Raised when generating embeddings fails."""


class EmbeddingService:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            base_url=settings.EMBEDDING_BASE_URL,
            api_key=settings.EMBEDDING_API_KEY,
        )

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            response = await self._client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except OpenAIError as error:
            raise EmbeddingError("Failed to generate embeddings") from error

    async def embed_query(self, query: str) -> list[float]:
        embeddings = await self.embed_texts([query])
        return embeddings[0]


_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

