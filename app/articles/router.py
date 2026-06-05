from typing import List, Optional

from fastapi import APIRouter, HTTPException, status

from app.articles.schemas import ArticleCreateSchema, ArticleSchema, ArticleSummarySchema, ArticleWriteSchema
from app.articles.service import ArticleService

router = APIRouter()
service = ArticleService()


@router.get("/{category_name}", response_model=List[ArticleSummarySchema])
def list_articles(category_name: str):
    articles = service.list(category=category_name)


@router.get("/{article_id}", response_model=ArticleSchema)
def get_article(article_id: str):
    pass


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_article(body: ArticleCreateSchema):
    article_id = service.create(body)
    if article_id:
        return {"id": article_id}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create article")

@router.put("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_article(article_id: str, body: ArticleWriteSchema):
    service.update(article_id, body)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: str):
    pass
