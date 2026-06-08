from typing import List

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import Response

from app.articles.schemas import ArticleContentSchema, ArticleCreateSchema, ArticleSchema, ArticleSummarySchema, ArticleWriteSchema
from app.articles.service import ArticleService

router = APIRouter()
service = ArticleService()


@router.get("/search", response_model=List[ArticleSummarySchema])
def search_articles(q: str = Query(default="")):
    return service.search(q)


@router.get("/{category_name}", response_model=List[ArticleSummarySchema])
def list_articles(category_name: str):
    return service.list(category=category_name)


@router.get("/{article_id}/document")
def get_article_document(article_id: str):
    binary = service.get_document(article_id)
    if binary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No stored document")
    return Response(content=binary, media_type="application/octet-stream")


@router.put("/{article_id}/document", status_code=status.HTTP_204_NO_CONTENT)
async def store_article_document(article_id: str, request: Request):
    binary = await request.body()
    service.store_document(article_id, binary)


@router.get("/{article_id}/content", response_model=ArticleContentSchema)
def get_article_content(article_id: str):
    return service.get_content(article_id)


@router.get("/{article_id}/references", response_model=List[ArticleSummarySchema])
def get_article_references(article_id: str):
    return service.get_references(article_id)


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
