"""Async SQLAlchemy engine, session factory, and declarative base."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from sta.config.settings import get_settings


class Base(DeclarativeBase):
    pass


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine() -> None:
    """Create the engine + session factory. Idempotent. Call once at startup."""
    global _engine, _session_factory
    if _engine is not None:
        return
    settings = get_settings()
    _engine = create_async_engine(settings.database_url)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def dispose_engine() -> None:
    """Dispose the engine. Call once at shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("Database engine not initialized; call init_engine() first")
    return _engine


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a request-scoped session."""
    if _session_factory is None:
        raise RuntimeError("Database engine not initialized; call init_engine() first")
    async with _session_factory() as session:
        yield session


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """Context manager for a DB session outside of FastAPI's dependency
    injection (module-internal code paths, e.g. Market Data's cold path)."""
    if _session_factory is None:
        raise RuntimeError("Database engine not initialized; call init_engine() first")
    async with _session_factory() as session:
        yield session
