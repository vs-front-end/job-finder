from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import router
from app.collectors import build_collectors
from app.config import load_config
from app.database import Repository
from app.pipeline import Pipeline
from app.services.scheduler import Scheduler

ROOT = Path(__file__).resolve().parents[1]


def create_app(
    config_path: Path | None = None, database_path: Path | None = None, start_scheduler: bool = True
) -> FastAPI:
    config_file = config_path or Path(os.getenv("JOB_FINDER_CONFIG", ROOT / "config.yaml"))
    database_file = database_path or Path(os.getenv("JOB_FINDER_DB", ROOT / "jobs.db"))
    config = load_config(config_file)
    repository = Repository(database_file)
    repository.initialize()
    collectors = build_collectors(config)
    pipeline = Pipeline(repository, config)
    scheduler = Scheduler(repository, pipeline, collectors, config)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        task = asyncio.create_task(scheduler.serve()) if start_scheduler else None
        yield
        scheduler.stop()
        if task:
            await task

    app = FastAPI(title="Job Finder", version="0.1.0", lifespan=lifespan)
    app.state.config = config
    app.state.config_path = config_file
    app.state.repository = repository
    app.state.collectors = collectors
    app.state.pipeline = pipeline
    app.state.scheduler = scheduler
    app.include_router(router)

    assets = ROOT / "web" / "dist" / "assets"
    index = ROOT / "web" / "dist" / "index.html"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        if index.exists():
            return FileResponse(index)
        return {"message": "Frontend not built yet. Run npm run build inside web/."}

    return app


app = create_app()


def run() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8787, reload=False)


if __name__ == "__main__":
    run()
