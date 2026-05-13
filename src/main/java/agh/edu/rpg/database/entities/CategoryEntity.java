package agh.edu.rpg.database.entities;

import org.springframework.data.neo4j.core.schema.GeneratedValue;
import org.springframework.data.neo4j.core.schema.Id;
import org.springframework.data.neo4j.core.schema.Node;
import org.springframework.data.neo4j.core.schema.Relationship;

import java.util.HashSet;
import java.util.Set;

@Node("Category")
public class CategoryEntity {

    @Id
    @GeneratedValue
    private Long id;

    private String name;

    @Relationship(type="CONTAINS_ARTICLE", direction = Relationship.Direction.OUTGOING)
    private Set<ArticleEntity> articles = new HashSet<>();

    public CategoryEntity() {
    }

    public CategoryEntity(String name) {
        this.name = name;
    }

    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public Set<ArticleEntity> getArticles() {
        return articles;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setArticles(Set<ArticleEntity> articles) {
        this.articles = articles;
    }

    public void addArticle(ArticleEntity article) {
        this.articles.add(article);
    }

}
