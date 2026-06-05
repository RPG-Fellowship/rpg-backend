from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import connect_db
from app.articles.router import router as articles_router
from app.categories.router import router as categories_router
from app.categories.model import CategoryNode

CATEGORY_NAMES = ["characters", "locations", "items", "quests", "maps"]


def seed_categories() -> None:
    '''
    Temporary function to seed the database with default categories present in the frontend.
    '''
    existing = {c.name for c in CategoryNode.match_nodes()}  # type: ignore[call-arg]
    for name in CATEGORY_NAMES:
        if name not in existing:
            CategoryNode(name=name).merge()


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_db()
    seed_categories()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

app.include_router(articles_router, prefix="/api/articles", tags=["articles"])
app.include_router(categories_router, prefix="/api/categories", tags=["categories"])
