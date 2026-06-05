from typing import ClassVar

from neontology import BaseRelationship

from app.articles.model import ArticleNode
from app.categories.model import CategoryNode


class ContainsArticleRelationship(BaseRelationship):
    """Category -[CONTAINS_ARTICLE]-> Article"""

    __relationshiptype__: ClassVar[str | None] = "CONTAINS_ARTICLE"

    source: CategoryNode # type: ignore[override]
    target: ArticleNode # type: ignore[override]
