"""Small SQLite telemetry store. Each event keeps the model that actually scored it."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from .schema import TelemetryEvent

STALE_AFTER_SECONDS = 5
EVENTS_PER_ASSET = 1000
MAX_ASSETS = 20


class ConflictError(ValueError):
    pass


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("""CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY, asset_id TEXT NOT NULL, timestamp TEXT NOT NULL,
                payload TEXT NOT NULL, result TEXT NOT NULL, received_at TEXT NOT NULL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS asset_time ON events(asset_id, timestamp)")

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def ingest(self, event: TelemetryEvent, predictor, now=None):
        now = now or datetime.now(UTC)
        if (event.timestamp - now).total_seconds() > 5:
            raise ValueError("Event timestamp is more than 5 seconds in the future")
        payload = event.model_dump_json()
        stamp = event.timestamp.isoformat(timespec="microseconds")
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                "SELECT * FROM events WHERE event_id=?", (event.event_id,)
            ).fetchone()
            if existing:
                if existing["payload"] != payload:
                    raise ConflictError("event_id already exists with different measurements")
                return {**json.loads(existing["result"]), "duplicate": True}
            latest = db.execute(
                "SELECT timestamp FROM events WHERE asset_id=? ORDER BY timestamp DESC LIMIT 1",
                (event.asset_id,),
            ).fetchone()
            if latest and stamp <= latest["timestamp"]:
                raise ConflictError("Asset timestamps must advance")
            if (
                not latest
                and db.execute("SELECT COUNT(DISTINCT asset_id) FROM events").fetchone()[0]
                >= MAX_ASSETS
            ):
                raise ValueError("Demo asset limit reached")
            result = predictor.predict(event)
            db.execute(
                "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?)",
                (
                    event.event_id,
                    event.asset_id,
                    stamp,
                    payload,
                    json.dumps(result, allow_nan=False),
                    now.isoformat(),
                ),
            )
            db.execute(
                """DELETE FROM events WHERE asset_id=? AND event_id NOT IN
                (SELECT event_id FROM events WHERE asset_id=? ORDER BY timestamp DESC LIMIT ?)""",
                (event.asset_id, event.asset_id, EVENTS_PER_ASSET),
            )
        return {**result, "duplicate": False}

    def assets(self):
        with self.connection() as db:
            return [
                row[0]
                for row in db.execute("SELECT DISTINCT asset_id FROM events ORDER BY asset_id")
            ]

    def snapshot(self, asset_id, now=None):
        now = now or datetime.now(UTC)
        with self.connection() as db:
            rows = db.execute(
                "SELECT * FROM events WHERE asset_id=? ORDER BY timestamp DESC LIMIT 120",
                (asset_id,),
            ).fetchall()
        events = [
            {
                "observation": json.loads(r["payload"]),
                "prediction": json.loads(r["result"]),
                "received_at": r["received_at"],
            }
            for r in reversed(rows)
        ]
        age = (
            max(0, (now - datetime.fromisoformat(rows[0]["timestamp"])).total_seconds())
            if rows
            else None
        )
        stale = age is None or age > STALE_AFTER_SECONDS
        return {
            "asset_id": asset_id,
            "events": events,
            "age_seconds": age,
            "stale": stale,
            "condition": "unknown" if stale else events[-1]["prediction"]["condition"],
            "stale_after_seconds": STALE_AFTER_SECONDS,
            "retention_per_asset": EVENTS_PER_ASSET,
        }
