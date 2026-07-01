"""Integration tests for Market Data API routes.

Requires `docker compose up -d` (Postgres + TimescaleDB and Redis).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient

from sta.api.main import app
from sta.core.types import Exchange
from sta.infrastructure.database import session_scope
from sta.modules.market_data.models import InstrumentModel


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    # NOTE: ASGITransport does not trigger FastAPI's lifespan — the _infra
    # autouse fixture (conftest.py) owns DB + Redis init/teardown for tests.
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=True),
        base_url="http://test",
    ) as c:
        yield c


@pytest.fixture(autouse=True)
async def _clean_instruments() -> AsyncIterator[None]:
    yield
    async with session_scope() as session:
        await session.execute(
            InstrumentModel.__table__.delete().where(
                InstrumentModel.instrument_token == 77777
            )
        )
        await session.commit()


async def test_list_instruments_empty(client: AsyncClient) -> None:
    response = await client.get("/market/instruments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_instrument_not_found(client: AsyncClient) -> None:
    response = await client.get("/market/instruments/99999")
    assert response.status_code == 404


async def test_session_state_nse(client: AsyncClient) -> None:
    response = await client.get("/market/session/NSE")
    assert response.status_code == 200
    data = response.json()
    assert data["exchange"] == "NSE"
    assert data["state"] in ("OPEN", "CLOSED", "PRE_OPEN", "HOLIDAY")


async def test_session_state_bse(client: AsyncClient) -> None:
    response = await client.get("/market/session/BSE")
    assert response.status_code == 200
    assert response.json()["exchange"] == "BSE"


async def test_get_ticks_empty(client: AsyncClient) -> None:
    response = await client.get("/market/ticks/99999")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_price_no_data(client: AsyncClient) -> None:
    response = await client.get("/market/price/NSE/FAKESYMBOL")
    assert response.status_code == 200
    data = response.json()
    assert data["exchange"] == "NSE"
    assert data["symbol"] == "FAKESYMBOL"
    assert data["last_price"] is None
    assert data["as_of"] is None


async def test_instrument_crud_via_api(client: AsyncClient) -> None:
    """Seed one instrument via ORM; verify it appears through the API."""
    async with session_scope() as session:
        session.add(
            InstrumentModel(
                instrument_token=77777,
                exchange=Exchange.NSE.value,
                symbol="TESTSTK",
                name="Test Stock",
                instrument_type="EQ",
                tick_size=Decimal("0.05"),
                lot_size=1,
            )
        )
        await session.commit()

    response = await client.get("/market/instruments/77777")
    assert response.status_code == 200
    assert response.json()["symbol"] == "TESTSTK"

    response = await client.get("/market/instruments?exchange=NSE")
    assert response.status_code == 200
    assert any(i["instrument_token"] == 77777 for i in response.json())
