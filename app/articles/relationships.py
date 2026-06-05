from typing import ClassVar

from neontology import BaseRelationship

from app.articles.model import ArticleNode


class ReferencesRelationship(BaseRelationship):
    """Article -[REFERENCES]-> Article"""

    __relationshiptype__: ClassVar[str | None] = "REFERENCES"

    source: ArticleNode # type: ignore[override]
    target: ArticleNode # type: ignore[override]
