from typing import List, Optional

from app.categories.schemas import CategoryCreateSchema, CategorySchema


class CategoryService:
    def list(self, q: Optional[str] = None) -> List[CategorySchema]:
        pass

    def get(self, category_id: str) -> Optional[CategorySchema]:
        pass

    def create(self, dto: CategoryCreateSchema) -> CategorySchema:
        pass
