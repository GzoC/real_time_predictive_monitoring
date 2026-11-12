"""Small SQLite telemetry store. Each event keeps the model that actually scored it."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .schema import TelemetryEvent

STALE_AFTER_SECONDS = 5
EVENTS_PER_ASSET = 1000
MAX_ASSETS = 20
CONFIRM_SAMPLES = 2
RECOVER_SAMPLES = 2


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
            db.executescript("""
                CREATE TABLE IF NOT EXISTS alarm_state (
                    asset_id TEXT PRIMARY KEY, last_timestamp TEXT NOT NULL,
                    alarm_count INTEGER NOT NULL, normal_count INTEGER NOT NULL,
                    active_episode TEXT
                );
                CREATE TABLE IF NOT EXISTS episodes (
                    episode_id TEXT PRIMARY KEY, asset_id TEXT NOT NULL,
                    opened_at TEXT NOT NULL, closed_at TEXT
                );
                CREATE TABLE IF NOT EXISTS drafts (
                    draft_id TEXT PRIMARY KEY, episode_id TEXT NOT NULL UNIQUE,
                    asset_id TEXT NOT NULL, created_at TEXT NOT NULL,
                    model_id TEXT NOT NULL, reason TEXT NOT NULL, evidence TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'draft', revision INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS draft_changes (
                    change_id INTEGER PRIMARY KEY, draft_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL, reviewer TEXT NOT NULL,
                    old_status TEXT, new_status TEXT NOT NULL, note TEXT NOT NULL,
                    revision INTEGER NOT NULL, UNIQUE(draft_id, revision)
                );
            """)

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
                if (
                    TelemetryEvent.model_validate_json(existing["payload"]).model_dump_json()
                    != payload
                ):
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
            if event.quality == "good":
                result = predictor.predict(event)
            else:
                result = {
                    "condition": "invalid",
                    "score": None,
                    "threshold": None,
                    "model_id": predictor.metadata["model_id"],
                    "out_of_training_range": [],
                    "task": "not_scored_quality",
                }
            # State, observation, evidence and draft commit in the same transaction.
            result["episode_id"] = self._advance_alarm(db, event, result, now)
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
            alarm = db.execute("SELECT * FROM alarm_state WHERE asset_id=?", (asset_id,)).fetchone()
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
            "alarm": dict(alarm) if alarm else None,
            "confirmation_samples": CONFIRM_SAMPLES,
            "recovery_samples": RECOVER_SAMPLES,
        }

    def _advance_alarm(self, db, event, result, now):
        previous = db.execute(
            "SELECT * FROM alarm_state WHERE asset_id=?", (event.asset_id,)
        ).fetchone()
        alarms = previous["alarm_count"] if previous else 0
        normals = previous["normal_count"] if previous else 0
        active = previous["active_episode"] if previous else None
        if (
            previous
            and (
                event.timestamp - datetime.fromisoformat(previous["last_timestamp"])
            ).total_seconds()
            > STALE_AFTER_SECONDS
        ):
            alarms = normals = 0
        # Stale or untrustworthy samples cannot confirm or clear an episode.
        usable = (
            event.quality == "good"
            and (now - event.timestamp).total_seconds() <= STALE_AFTER_SECONDS
        )
        if not usable:
            alarms = normals = 0
        elif result["condition"] == "alarm":
            alarms = min(alarms + 1, CONFIRM_SAMPLES)
            normals = 0
            if not active and alarms >= CONFIRM_SAMPLES:
                active = uuid4().hex
                draft = "draft-" + active
                db.execute(
                    "INSERT INTO episodes VALUES (?, ?, ?, NULL)",
                    (active, event.asset_id, event.timestamp.isoformat()),
                )
                evidence = {
                    "confirmation_event_id": event.event_id,
                    "confirmation_samples": CONFIRM_SAMPLES,
                    "preceding_measurement": json.loads(
                        db.execute(
                            "SELECT payload FROM events WHERE asset_id=? ORDER BY timestamp DESC LIMIT 1",
                            (event.asset_id,),
                        ).fetchone()[0]
                    ),
                    "measurement": event.model_dump(mode="json"),
                    "prediction": result,
                }
                db.execute(
                    """INSERT INTO drafts
                    (draft_id, episode_id, asset_id, created_at, model_id, reason, evidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        draft,
                        active,
                        event.asset_id,
                        now.isoformat(),
                        result["model_id"],
                        "Current-condition classifier exceeded threshold in two consecutive fresh good-quality samples; inspect measurements before deciding maintenance.",
                        json.dumps(evidence, allow_nan=False),
                    ),
                )
                db.execute(
                    """INSERT INTO draft_changes
                    (draft_id, timestamp, reviewer, old_status, new_status, note, revision)
                    VALUES (?, ?, 'local-adapter', NULL, 'draft', 'Simulated draft created; no external order sent', 0)""",
                    (draft, now.isoformat()),
                )
        elif result["condition"] == "normal":
            normals = min(normals + 1, RECOVER_SAMPLES)
            alarms = 0
            if active and normals >= RECOVER_SAMPLES:
                db.execute(
                    "UPDATE episodes SET closed_at=? WHERE episode_id=?",
                    (event.timestamp.isoformat(), active),
                )
                active = None
        db.execute(
            "INSERT OR REPLACE INTO alarm_state VALUES (?, ?, ?, ?, ?)",
            (event.asset_id, event.timestamp.isoformat(), alarms, normals, active),
        )
        return active

    def drafts(self, asset_id):
        with self.connection() as db:
            rows = db.execute(
                """SELECT d.*, e.opened_at, e.closed_at FROM drafts d
                JOIN episodes e USING(episode_id) WHERE d.asset_id=? ORDER BY d.created_at DESC""",
                (asset_id,),
            ).fetchall()
            output = []
            for row in rows:
                item = dict(row)
                item["evidence"] = json.loads(item["evidence"])
                item["changes"] = [
                    dict(change)
                    for change in db.execute(
                        "SELECT * FROM draft_changes WHERE draft_id=? ORDER BY revision",
                        (row["draft_id"],),
                    )
                ]
                output.append(item)
            return output

    def review(self, draft_id, review, now=None):
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM drafts WHERE draft_id=?", (draft_id,)).fetchone()
            if row is None:
                raise KeyError(draft_id)
            if row["revision"] != review.expected_revision:
                raise ConflictError("Draft changed; reload before reviewing")
            revision = row["revision"] + 1
            db.execute(
                "UPDATE drafts SET status=?, revision=? WHERE draft_id=?",
                (review.status, revision, draft_id),
            )
            db.execute(
                """INSERT INTO draft_changes
                (draft_id, timestamp, reviewer, old_status, new_status, note, revision)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    draft_id,
                    (now or datetime.now(UTC)).isoformat(),
                    review.reviewer,
                    row["status"],
                    review.status,
                    review.note,
                    revision,
                ),
            )
        return {
            "draft_id": draft_id,
            "status": review.status,
            "revision": revision,
            "external_dispatch": False,
        }
