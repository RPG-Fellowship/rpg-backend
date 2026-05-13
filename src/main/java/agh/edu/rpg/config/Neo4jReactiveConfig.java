package agh.edu.rpg.config;

import org.neo4j.driver.Driver;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.neo4j.core.ReactiveDatabaseSelectionProvider;
import org.springframework.data.neo4j.core.transaction.ReactiveNeo4jTransactionManager;
import org.springframework.data.neo4j.repository.config.EnableReactiveNeo4jRepositories;
import org.springframework.transaction.ReactiveTransactionManager;

@Configuration
@EnableReactiveNeo4jRepositories(basePackages = "agh.edu.rpg.repositories")
public class Neo4jReactiveConfig {

    @Bean
    public ReactiveDatabaseSelectionProvider reactiveDatabaseSelectionProvider(
            @Value("${spring.data.neo4j.database:neo4j}") String database) {
        return ReactiveDatabaseSelectionProvider.createStaticDatabaseSelectionProvider(database);
    }

    @Bean(name = "reactiveTransactionManager")
    public ReactiveTransactionManager reactiveTransactionManager(
            Driver driver,
            ReactiveDatabaseSelectionProvider databaseSelectionProvider) {
        return new ReactiveNeo4jTransactionManager(driver, databaseSelectionProvider);
    }
}
