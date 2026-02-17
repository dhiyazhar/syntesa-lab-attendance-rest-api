import logging
from contextlib import asynccontextmanager
from typing import Annotated

from curl_cffi.requests import AsyncSession
from database import create_db_and_tables, get_session
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from routers import attendance
from sqlmodel import Session

SessionDep = Annotated[Session, Depends(get_session)]
logger = logging.getLogger("uvicorn.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    scraper = AsyncSession(impersonate="chrome110")
    logger.info("We got a new session, ladiez!")
    app.state.pdunesa_session = scraper

    yield
    await scraper.close()


async def get_scraper(request: Request):
    return request.app.state.pdunesa_session


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api/v1")
router.include_router(attendance.router)
app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Hello, World!"}

