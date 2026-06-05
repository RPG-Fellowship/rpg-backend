from typing import List, Optional

from fastapi import APIRouter, status

from app.categories.schemas import CategoryCreateSchema, CategorySchema
from app.categories.service import CategoryService

router = APIRouter()
service = CategoryService()


@router.get("", response_model=List[CategorySchema])
def list_categories(q: Optional[str] = None):
    pass


@router.get("/{category_id}", response_model=CategorySchema)
def get_category(category_id: str):
    pass


@router.post("", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
def create_category(body: CategoryCreateSchema):
    pass
