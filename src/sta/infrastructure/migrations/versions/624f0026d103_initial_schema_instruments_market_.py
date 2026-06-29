"""initial schema: instruments, market_sessions, ticks hypertable

Revision ID: 624f0026d103
Revises:
Create Date: 2026-06-29 14:47:18.820572

Continuous aggregates (bars_1m, bars_5m) are deferred to a follow-up
migration per architecture decision A3 — they can't run inside a
transaction, which fights Alembic's transactional DDL.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "624f0026d103"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")

    op.create_table(
        "instruments",
        sa.Column("instrument_token", sa.BigInteger(), primary_key=True),
        sa.Column("exchange", sa.String(length=8), nullable=False),
        sa.Column("symbol", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("instrument_type", sa.String(length=16), nullable=False),
        sa.Column("tick_size", sa.Numeric(12, 4), nullable=False),
        sa.Column("lot_size", sa.BigInteger(), nullable=False),
        sa.Column("expiry", sa.Date(), nullable=True),
    )
    op.create_index("ix_instruments_symbol", "instruments", ["symbol"])

    op.create_table(
        "market_sessions",
        sa.Column("session_date", sa.Date(), primary_key=True),
        sa.Column("exchange", sa.String(length=8), primary_key=True),
        sa.Column("is_holiday", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("pre_open_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("open_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("close_time", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "ticks",
        sa.Column("time", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("instrument_token", sa.BigInteger(), primary_key=True),
        sa.Column("exchange", sa.String(length=8), nullable=False),
        sa.Column("symbol", sa.String(length=64), nullable=False),
        sa.Column("last_price", sa.Numeric(12, 4), nullable=False),
        sa.Column("last_traded_quantity", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("volume_traded", sa.BigInteger(), nullable=False, server_default="0"),
    )
    op.execute("SELECT create_hypertable('ticks', 'time');")


def downgrade() -> None:
    op.drop_table("ticks")
    op.drop_table("market_sessions")
    op.drop_index("ix_instruments_symbol", table_name="instruments")
    op.drop_table("instruments")
