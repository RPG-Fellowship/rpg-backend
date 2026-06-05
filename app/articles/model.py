from typing import ClassVar, Optional
from uuid import uuid4

from neontology import BaseNode
from pydantic import Field


class ArticleNode(BaseNode):
    __primarylabel__: ClassVar[str | None] = "Article"
    __primaryproperty__: ClassVar[str] = "article_id"

    article_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    content: Optional[str] = None
