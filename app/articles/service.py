from typing import List, Optional

from app.articles.schemas import ArticleCreateSchema, ArticleSchema, ArticleSummarySchema, ArticleWriteSchema
from app.articles.model import ArticleNode
from app.articles.exceptions import ArticleNotFoundException    
from app.categories.model import CategoryNode
from app.categories.relationships import ContainsArticleRelationship


class ArticleService:
    def list(self, category: str) -> List[ArticleSummarySchema]:
        category_node = CategoryNode.match_nodes(filters={"name": category})
        if len(category_node) == 0 or len(category_node) > 1:
            raise ValueError("Category not found or multiple categories with the same name exist")
        category_node = category_node[0]
        articles = category_node.get_related( # 
            relationship_types=["CONTAINS_ARTICLE"],
        ).nodes
        return [ArticleSummarySchema(id=article.article_id, title=article.title) for article in articles]

    def get(self, article_id: str) -> Optional[ArticleSchema]:
        pass

    def create(self, dto: ArticleCreateSchema) -> str:
        category = CategoryNode.match_nodes(
            filters={"name": dto.category}
        )
        if len(category) == 0 or len(category) > 1:
            raise ValueError("Category not found or multiple categories with the same name exist")
        category = category[0]
        article = ArticleNode(title="untitled", content="")
        article.create()
        rel = ContainsArticleRelationship(source=category, target=article)
        rel.merge()

        return article.article_id

    def update(self, article_id: str, dto: ArticleWriteSchema) -> Optional[ArticleSchema]:
        article = ArticleNode.match(article_id)
        if article:
            updated = article.model_copy(
                update={
                    "title": dto.title,
                    "content": dto.content
                }
            )
            updated.merge()
        else:
            raise ArticleNotFoundException()
            
    def delete(self, article_id: str) -> None:
        pass
