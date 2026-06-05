from typing import ClassVar
from uuid import uuid4

from neontology import BaseNode
from pydantic import Field


class CategoryNode(BaseNode):
    __primarylabel__: ClassVar[str | None] = "Category"
    __primaryproperty__: ClassVar[str] = "category_id"

    category_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
