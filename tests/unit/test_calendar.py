"""Unit tests for calendar.resolve_state — pure session-state resolution."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sta.modules.market_data.calendar import SessionInfo, SessionState, resolve_state


def _info(pre_open: datetime, open_: datetime, close: datetime) -> SessionInfo:
    return SessionInfo(is_holiday=False, pre_open_start=pre_open, open_time=open_, close_time=close)


def test_resolve_state_holiday() -> None:
    info = SessionInfo(is_holiday=True, pre_open_start=None, open_time=None, close_time=None)
    assert resolve_state(info, datetime.now(timezone.utc)) == SessionState.HOLIDAY


def test_resolve_state_before_pre_open() -> None:
    base = datetime(2026, 1, 5, 0, 0, tzinfo=timezone.utc)
    info = _info(base + timedelta(hours=3), base + timedelta(hours=4), base + timedelta(hours=10))
    assert resolve_state(info, base) == SessionState.CLOSED


def test_resolve_state_pre_open_window() -> None:
    base = datetime(2026, 1, 5, 0, 0, tzinfo=timezone.utc)
    info = _info(base, base + timedelta(hours=1), base + timedelta(hours=6))
    assert resolve_state(info, base + timedelta(minutes=30)) == SessionState.PRE_OPEN


def test_resolve_state_open_window() -> None:
    base = datetime(2026, 1, 5, 0, 0, tzinfo=timezone.utc)
    info = _info(base, base + timedelta(hours=1), base + timedelta(hours=6))
    assert resolve_state(info, base + timedelta(hours=2)) == SessionState.OPEN


def test_resolve_state_after_close() -> None:
    base = datetime(2026, 1, 5, 0, 0, tzinfo=timezone.utc)
    info = _info(base, base + timedelta(hours=1), base + timedelta(hours=6))
    assert resolve_state(info, base + timedelta(hours=7)) == SessionState.CLOSED
