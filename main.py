from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from config import settings
from routers import auth, google_auth, health, notes


def create_app() -> FastAPI:
    """Application factory keeps startup wiring easy to scan and test."""

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(google_auth.router)
    app.include_router(notes.router)

    return app


app = create_app()
