from typing import List, Optional

from pydantic import BaseModel


class ArticleSummarySchema(BaseModel):
    id: str
    title: str


class ArticleSchema(BaseModel):
    id: str
    title: str
    content: Optional[str]
    references: List[ArticleSummarySchema]


class ArticleCreateSchema(BaseModel):
    category: str


class ArticleWriteSchema(BaseModel):
    title: str
    content: str
