package agh.edu.rpg.database.entities;

import agh.edu.rpg.database.relationships.References;
import org.springframework.data.neo4j.core.schema.GeneratedValue;
import org.springframework.data.neo4j.core.schema.Id;
import org.springframework.data.neo4j.core.schema.Node;
import org.springframework.data.neo4j.core.schema.Relationship;

import java.util.HashSet;
import java.util.Set;

@Node("Article")
public class ArticleEntity {

    @Id
    @GeneratedValue
    private Long id;

    private String title;

    private String content;

    @Relationship(type = "REFERENCES")
    private Set<References> referencedArticles = new HashSet<>();

    public ArticleEntity() {
    }

    public ArticleEntity(String title) {
        this.title = title;
    }

    public void setReferencedArticles(Set<References> referencedArticles) {
        this.referencedArticles = referencedArticles;
    }

    public Long getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getContent() {
        return content;
    }

    public Set<References> getReferencedArticles() {
        return referencedArticles;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public void addReferencedArticle(References referencedArticle) {
        this.referencedArticles.add(referencedArticle);
    }

    public void removeReferencedArticle(References referencedArticle) {
        this.referencedArticles.remove(referencedArticle);
    }

    public void setTitle(String title) {
        this.title = title;
    }
}
