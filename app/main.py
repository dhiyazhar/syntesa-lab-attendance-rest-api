import logging
from contextlib import asynccontextmanager
from curl_cffi.requests import AsyncSession
from fastapi import  APIRouter, Depends, FastAPI, Request
from typing import Annotated
from sqlmodel import Session

from database import get_session, create_db_and_tables
from routers import attendance

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

router = APIRouter(prefix="/api/v1")
router.include_router(attendance.router)
app.include_router(router)

@app.get("/")    
async def root():
    return {"message": "Hello, World!"}