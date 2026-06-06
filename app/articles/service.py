from typing import List, Optional

from app.articles.schemas import ArticleContentSchema, ArticleCreateSchema, ArticleSchema, ArticleSummarySchema, ArticleWriteSchema
from app.articles.model import ArticleNode
from app.articles.exceptions import ArticleNotFoundException
from app.categories.model import CategoryNode
from app.categories.relationships import ContainsArticleRelationship
from app.storage import S3ClientProvider


class ArticleService:
    def list(self, category: str) -> List[ArticleSummarySchema]:
        """List articles in a specific category.

        Args:
            category (str): The name of the category to list articles from.

        Raises:
            ValueError: If the category is not found or if multiple categories with the same name exist.

        Returns:
            List[ArticleSummarySchema]: A list of article summaries in the specified category.
        """
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
        """Retrieve the content of a specific article.

        Args:
            article_id (str): The ID of the article to retrieve content for.

        Raises:
            ArticleNotFoundException: If the article with the specified ID is not found.

        Returns:
            ArticleContentSchema: The content of the specified article.
        """
        article = ArticleNode.match(article_id)
        if not article:
            raise ArticleNotFoundException()
        content = S3ClientProvider.load_article_json(article_id)
        return ArticleContentSchema(title=article.title, content=content)

    def create(self, dto: ArticleCreateSchema) -> str:
        """Creates a new empty article in the specified category.

        Args:
            dto (ArticleCreateSchema): The data for creating the article.

        Raises:
            ValueError: If the category is not found or if multiple categories with the same name exist.

        Returns:
            str: The ID of the created article.
        """
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
        """Updates article content in periodic saves.

        Args:
            article_id (str): The ID of the article to update.
            dto (ArticleWriteSchema): The data for updating the article.

        Raises:
            ArticleNotFoundException: If the article with the specified ID is not found.
        """
        article = ArticleNode.match(article_id)
        if not article:
            raise ArticleNotFoundException()
        content_key = S3ClientProvider.store_article_json(article_id, dto.content)
        article.model_copy(update={"title": dto.title, "content_key": content_key}).merge()

    def store_document(self, article_id: str, binary: bytes) -> str:
        return S3ClientProvider.store_article_bin(article_id, binary)

    def get_document(self, article_id: str) -> bytes | None:
        return S3ClientProvider.load_article_bin(article_id)

    def delete(self, article_id: str) -> None:
        pass
