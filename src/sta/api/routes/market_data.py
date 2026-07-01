"""Market Data API — REST read endpoints and WebSocket live tick stream."""

from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sta.core.types import Exchange
from sta.infrastructure.database import get_session
from sta.infrastructure.redis_client import get_latest_price, subscribe
from sta.modules.market_data.calendar import SessionState, current_session_state
from sta.modules.market_data.hot_path import tick_channel
from sta.modules.market_data.models import InstrumentModel, TickModel

# API / MARKET: Market Data read endpoints + WebSocket live tick stream.

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["market-data"])


# --- Response schemas -------------------------------------------------------


class InstrumentOut(BaseModel):
    instrument_token: int
    exchange: str
    symbol: str
    name: str
    instrument_type: str
    tick_size: Decimal
    lot_size: int
    expiry: date | None = None

    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    exchange: str
    state: SessionState


class TickOut(BaseModel):
    time: datetime
    instrument_token: int
    exchange: str
    symbol: str
    last_price: Decimal
    last_traded_quantity: int
    volume_traded: int

    model_config = {"from_attributes": True}


class PriceOut(BaseModel):
    exchange: str
    symbol: str
    last_price: str | None
    as_of: str | None


# --- Endpoints ---------------------------------------------------------------


@router.get("/instruments", response_model=list[InstrumentOut])
async def list_instruments(
    exchange: Exchange | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[InstrumentModel]:
    """List all instruments, optionally filtered by exchange."""
    stmt = select(InstrumentModel)
    if exchange is not None:
        stmt = stmt.where(InstrumentModel.exchange == exchange.value)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get("/instruments/{instrument_token}", response_model=InstrumentOut)
async def get_instrument(
    instrument_token: int,
    session: AsyncSession = Depends(get_session),
) -> InstrumentModel:
    """Get a single instrument by token."""
    result = await session.execute(
        select(InstrumentModel).where(
            InstrumentModel.instrument_token == instrument_token
        )
    )
    instrument = result.scalar_one_or_none()
    if instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return instrument


@router.get("/session/{exchange}", response_model=SessionOut)
async def get_session_state(exchange: Exchange) -> SessionOut:
    """Current trading session state (OPEN / PRE_OPEN / CLOSED / HOLIDAY)."""
    state = await current_session_state(exchange)
    return SessionOut(exchange=exchange.value, state=state)


@router.get("/ticks/{instrument_token}", response_model=list[TickOut])
async def get_ticks(
    instrument_token: int,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
) -> list[TickModel]:
    """Return the most recent ticks for an instrument (newest first). Max 1000."""
    result = await session.execute(
        select(TickModel)
        .where(TickModel.instrument_token == instrument_token)
        .order_by(TickModel.time.desc())
        .limit(min(limit, 1000))
    )
    return list(result.scalars().all())


@router.get("/price/{exchange}/{symbol}", response_model=PriceOut)
async def get_price(exchange: Exchange, symbol: str) -> PriceOut:
    """Latest cached price for an instrument (from the Redis hot path)."""
    data = await get_latest_price(exchange.value, symbol.upper())
    return PriceOut(
        exchange=exchange.value,
        symbol=symbol.upper(),
        last_price=data.get("last_price"),
        as_of=data.get("timestamp"),
    )


@router.websocket("/ws/ticks/{exchange}/{symbol}")
async def tick_stream(websocket: WebSocket, exchange: Exchange, symbol: str) -> None:
    """Stream live ticks for an instrument (one JSON message per tick)."""
    await websocket.accept()
    channel = tick_channel(exchange.value, symbol.upper())
    logger.info("ws connected channel=%s", channel)
    try:
        async for payload in subscribe(channel):
            await websocket.send_text(payload)
    except WebSocketDisconnect:
        pass
    finally:
        logger.info("ws disconnected channel=%s", channel)
