"""Limitador de tentativas de login por e-mail."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .clock import Clock, now_brt

MAX_FAILURES = 5
WINDOW = timedelta(minutes=15)
LOCKOUT = timedelta(minutes=5)


@dataclass
class _Record:
    failures: list[datetime] = field(default_factory=list)
    locked_until: datetime | None = None


class LoginThrottle:
    """Após ``MAX_FAILURES`` falhas em ``WINDOW``, bloqueia o e-mail por ``LOCKOUT``."""

    def __init__(self, clock: Clock = now_brt) -> None:
        self._clock = clock
        self._records: dict[str, _Record] = {}

    @staticmethod
    def _key(email: str) -> str:
        return email.strip().casefold()

    def remaining_lock(self, email: str) -> timedelta | None:
        record = self._records.get(self._key(email))
        if record is None or record.locked_until is None:
            return None
        now = self._clock()
        if now >= record.locked_until:
            self._records.pop(self._key(email), None)
            return None
        return record.locked_until - now

    def remaining_minutes(self, email: str) -> int:
        remaining = self.remaining_lock(email)
        return math.ceil(remaining.total_seconds() / 60) if remaining else 0

    def register_failure(self, email: str) -> None:
        now = self._clock()
        record = self._records.setdefault(self._key(email), _Record())
        record.failures = [t for t in record.failures if now - t < WINDOW] + [now]
        if len(record.failures) >= MAX_FAILURES:
            record.locked_until = now + LOCKOUT
            record.failures = []

    def register_success(self, email: str) -> None:
        self._records.pop(self._key(email), None)
