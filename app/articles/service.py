import json
from typing import List, Optional

from neontology import GraphConnection

from app.articles.schemas import ArticleContentSchema, ArticleCreateSchema, ArticleSchema, ArticleSummarySchema, ArticleWriteSchema
from app.articles.model import ArticleNode
from app.articles.exceptions import ArticleNotFoundException
from app.articles.relationships import ReferencesRelationship
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

    def search(self, q: str) -> List[ArticleSummarySchema]:
        """Search articles by title prefix (case-insensitive).

        Args:
            q (str): The prefix string to match against article titles.

        Returns:
            List[ArticleSummarySchema]: All articles whose title starts with the given prefix.
        """
        gc = GraphConnection()
        result = gc.evaluate_query(
            "MATCH (a:Article) WHERE toLower(a.title) STARTS WITH toLower($q) RETURN a",
            {"q": q},
        )
        return [
            ArticleSummarySchema(id=node.article_id, title=node.title)
            for node in result.nodes
            if isinstance(node, ArticleNode)
        ]

    def get_references(self, article_id: str) -> List[ArticleSummarySchema]:
        """Return all articles referenced (mentioned) by the given article.

        Args:
            article_id (str): The ID of the source article.

        Returns:
            List[ArticleSummarySchema]: Articles linked via outgoing REFERENCES relationships.
        """
        gc = GraphConnection()
        result = gc.evaluate_query(
            "MATCH (a:Article {article_id: $id})-[:REFERENCES]->(t:Article) RETURN t",
            {"id": article_id},
        )
        return [
            ArticleSummarySchema(id=node.article_id, title=node.title)
            for node in result.nodes
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
        category = CategoryNode.match_nodes(filters={"name": dto.category})
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

        if dto.content:
            try:
                content_dict = json.loads(dto.content)
                mention_ids = self._extract_mention_ids(content_dict)
                self._sync_mentions(article_id, mention_ids)
            except (json.JSONDecodeError, KeyError):
                pass

    def _extract_mention_ids(self, node: dict) -> List[str]:
        """Recursively extract article IDs from mention nodes in a TipTap JSON document.

        Args:
            node (dict): A TipTap JSON node (or the root document dict).

        Returns:
            List[str]: All article IDs found in mention nodes within the document tree.
        """
        ids: List[str] = []
        if node.get("type") == "mention" and node.get("attrs", {}).get("id"):
            ids.append(node["attrs"]["id"])
        for child in node.get("content", []):
            ids.extend(self._extract_mention_ids(child))
        return ids

    def _sync_mentions(self, article_id: str, new_ids: List[str]) -> None:
        """Incrementally sync REFERENCES relationships for an article based on its current mentions.

        Compares the provided mention IDs against existing REFERENCES edges in the database
        and adds or removes relationships to match the new set.

        Args:
            article_id (str): The ID of the source article whose mentions changed.
            new_ids (List[str]): Article IDs currently mentioned in the document.
        """
        gc = GraphConnection()

        current_ids: set = set(
            gc.evaluate_query_single(
                "MATCH (a:Article {article_id: $id})-[:REFERENCES]->(t:Article) RETURN collect(t.article_id)",
                {"id": article_id},
            )
            or []
        )

        new_id_set = set(new_ids)
        to_add = new_id_set - current_ids
        to_remove = current_ids - new_id_set

        source = ArticleNode.match(article_id)
        if not source:
            return

        for target_id in to_add:
            target = ArticleNode.match(target_id)
            if target:
                ReferencesRelationship(source=source, target=target).merge()

        if to_remove:
            gc.evaluate_query_single(
                "MATCH (a:Article {article_id: $sid})-[r:REFERENCES]->(t:Article)"
                " WHERE t.article_id IN $remove_ids DELETE r RETURN count(r)",
                {"sid": article_id, "remove_ids": list(to_remove)},
            )

    def store_document(self, article_id: str, binary: bytes) -> str:
        return S3ClientProvider.store_article_bin(article_id, binary)

    def get_document(self, article_id: str) -> bytes | None:
        return S3ClientProvider.load_article_bin(article_id)

    def delete(self, article_id: str) -> None:
        pass
