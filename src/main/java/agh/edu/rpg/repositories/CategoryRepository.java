package agh.edu.rpg.repositories;

import agh.edu.rpg.database.entities.CategoryEntity;
import org.springframework.data.neo4j.repository.ReactiveNeo4jRepository;
import reactor.core.publisher.Flux;

public interface CategoryRepository extends ReactiveNeo4jRepository<CategoryEntity, Long> {

    Flux<CategoryEntity> findAllByNameContainingIgnoreCaseOrderByNameAsc(String q);
}
