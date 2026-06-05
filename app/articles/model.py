from typing import ClassVar, Optional
from uuid import uuid4

from neontology import BaseNode
from pydantic import ConfigDict, Field


class ArticleNode(BaseNode):
    model_config = ConfigDict(extra="ignore")

    __primarylabel__: ClassVar[str | None] = "Article"
    __primaryproperty__: ClassVar[str] = "article_id"

    article_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    content_key: Optional[str] = None
