package agh.edu.rpg.database.relationships;

import agh.edu.rpg.database.entities.ArticleEntity;
import org.springframework.data.neo4j.core.schema.GeneratedValue;
import org.springframework.data.neo4j.core.schema.Id;
import org.springframework.data.neo4j.core.schema.RelationshipProperties;
import org.springframework.data.neo4j.core.schema.TargetNode;

@RelationshipProperties
public class References {

    @Id
    @GeneratedValue
    private Long id;

    @TargetNode
    private ArticleEntity targetArticle;

    public References(ArticleEntity targetArticle) {
        this.targetArticle = targetArticle;
    }

    public Long getId() {
        return id;
    }

    public ArticleEntity getTargetArticle() {
        return targetArticle;
    }
}
