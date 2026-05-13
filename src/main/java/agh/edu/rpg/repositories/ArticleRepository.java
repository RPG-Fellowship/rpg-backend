package agh.edu.rpg.repositories;

import agh.edu.rpg.database.entities.ArticleEntity;
import org.springframework.data.neo4j.repository.ReactiveNeo4jRepository;
import reactor.core.publisher.Flux;

public interface ArticleRepository extends ReactiveNeo4jRepository<ArticleEntity, Long> {

    Flux<ArticleEntity> findTop10ByTitleContainingIgnoreCaseOrderByTitleAsc(String q);
}
