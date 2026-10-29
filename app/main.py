import importlib
import pkgutil
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import routers

app = FastAPI(title="colonIA")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# `routers` (not `app.routers`): the `app` variable shadows the package of the same name.
for module in pkgutil.iter_modules(routers.__path__):
    router = getattr(importlib.import_module(f"{routers.__name__}.{module.name}"), "router", None)
    if router is not None:
        app.include_router(router)

# The frontend build is mounted last: /api/* and /n/* always win over static files.
WEB_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"
if WEB_DIST.is_dir():
    app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="web")
