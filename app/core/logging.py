from contextvars import ContextVar, Token
from time import perf_counter

_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(request_id: str) -> Token[str | None]:
    return _request_id_ctx.set(request_id)


def reset_request_id(token: Token[str | None]) -> None:
    _request_id_ctx.reset(token)


def get_request_id() -> str | None:
    return _request_id_ctx.get()


def elapsed_ms(started_at: float) -> float:
    return round((perf_counter() - started_at) * 1000.0, 2)

