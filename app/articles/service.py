from typing import List, Optional

from app.articles.schemas import ArticleContentSchema, ArticleCreateSchema, ArticleSchema, ArticleSummarySchema, ArticleWriteSchema
from app.articles.model import ArticleNode
from app.articles.exceptions import ArticleNotFoundException
from app.categories.model import CategoryNode
from app.categories.relationships import ContainsArticleRelationship
from app.storage import load_article_content, load_article_document, store_article_content, store_document as _store_document


class ArticleService:
    def list(self, category: str) -> List[ArticleSummarySchema]:
        category_node = CategoryNode.match_nodes(filters={"name": category})
        if len(category_node) == 0 or len(category_node) > 1:
            raise ValueError("Category not found or multiple categories with the same name exist")
        category_node = category_node[0]
        articles = category_node.get_related(
            relationship_types=["CONTAINS_ARTICLE"],
        ).nodes
        return [
            ArticleSummarySchema(id=node.article_id, title=node.title)
            for node in articles
            if isinstance(node, ArticleNode)
        ]

    def get(self, article_id: str) -> Optional[ArticleSchema]:
        pass

    def get_content(self, article_id: str) -> ArticleContentSchema:
        article = ArticleNode.match(article_id)
        if not article:
            raise ArticleNotFoundException()
        content = load_article_content(article_id)
        return ArticleContentSchema(title=article.title, content=content)

    def create(self, dto: ArticleCreateSchema) -> str:
        category = CategoryNode.match_nodes(
            filters={"name": dto.category}
        )
        if len(category) == 0 or len(category) > 1:
            raise ValueError("Category not found or multiple categories with the same name exist")
        category = category[0]
        article = ArticleNode(title="untitled")
        article.create()
        rel = ContainsArticleRelationship(source=category, target=article)
        rel.merge()

        return article.article_id

    def update(self, article_id: str, dto: ArticleWriteSchema) -> None:
        article = ArticleNode.match(article_id)
        if not article:
            raise ArticleNotFoundException()
        content_key = store_article_content(article_id, dto.content)
        article.model_copy(update={"title": dto.title, "content_key": content_key}).merge()

    def store_document(self, article_id: str, binary: bytes) -> None:
        _store_document(article_id, binary)

    def get_document(self, article_id: str) -> bytes | None:
        return load_article_document(article_id)

    def delete(self, article_id: str) -> None:
        pass
