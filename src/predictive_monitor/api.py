"""Application factory keeps a missing model observable without hiding inference failures."""

import logging
import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .inference import Predictor
from .schema import Observation, TelemetryEvent
from .storage import ConflictError, Store

logger = logging.getLogger(__name__)


def create_app(model_dir=None, db_path=None):
    directory = Path(model_dir or os.environ.get("MODEL_DIR", "var/model"))

    @asynccontextmanager
    async def lifespan(app):
        app.state.predictor = None
        app.state.store = None
        try:
            app.state.predictor = Predictor(directory)
            app.state.store = Store(db_path or os.environ.get("TELEMETRY_DB", "var/telemetry.db"))
        except Exception:
            logger.exception("Service initialization failed")
        yield

    app = FastAPI(title="Industrial condition monitor", version="0.2.0", lifespan=lifespan)

    @app.middleware("http")
    async def no_cache(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    def ready():
        if app.state.predictor is None or app.state.store is None:
            raise HTTPException(
                503, "Model or telemetry store unavailable; train and restart the service"
            )
        return app.state.predictor, app.state.store

    @app.exception_handler(sqlite3.Error)
    async def database_error(request, exc):
        logger.error("Telemetry database unavailable", exc_info=exc)
        return JSONResponse(status_code=503, content={"detail": "Telemetry storage unavailable"})

    @app.get("/health")
    def health():
        predictor, store = ready()
        with store.connection() as db:
            db.execute("SELECT 1").fetchone()
        return {"status": "ready", "model_id": predictor.metadata["model_id"]}

    @app.get("/model")
    def model():
        return ready()[0].metadata

    @app.post("/predict")
    def predict(observation: Observation):
        return ready()[0].predict(observation)

    @app.post("/events")
    def ingest(event: TelemetryEvent):
        predictor, store = ready()
        try:
            return store.ingest(event, predictor)
        except ConflictError as exc:
            raise HTTPException(409, str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/assets")
    def assets():
        return {"assets": ready()[1].assets()}

    @app.get("/assets/{asset_id}/snapshot")
    def snapshot(asset_id: str):
        return ready()[1].snapshot(asset_id)

    return app
