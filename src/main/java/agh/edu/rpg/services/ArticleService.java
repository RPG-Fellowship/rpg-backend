package agh.edu.rpg.services;

import agh.edu.rpg.database.entities.ArticleEntity;
import agh.edu.rpg.database.relationships.References;
import agh.edu.rpg.dto.ArticleDto;
import agh.edu.rpg.dto.ArticleSummaryDto;
import agh.edu.rpg.dto.ArticleWriteDto;
import agh.edu.rpg.repositories.ArticleRepository;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

@Service
public class ArticleService {

    private final ArticleRepository repository;
    private final ObjectMapper objectMapper;

    public ArticleService(ArticleRepository repository, ObjectMapper objectMapper) {
        this.repository = repository;
        this.objectMapper = objectMapper;
    }

    public Flux<ArticleSummaryDto> list(String q) {
        Flux<ArticleEntity> source = (q == null || q.isBlank())
                ? repository.findAll()
                : repository.findTop10ByTitleContainingIgnoreCaseOrderByTitleAsc(q.trim());
        return source.map(a -> new ArticleSummaryDto(a.getId(), a.getTitle()));
    }

    public Mono<ArticleDto> get(Long id) {
        return repository.findById(id).map(this::toDto);
    }

    public Mono<ArticleDto> create(ArticleWriteDto dto) {
        ArticleEntity entity = new ArticleEntity(dto.title());
        entity.setContent(dto.content());
        return assignReferences(entity, dto.content())
                .flatMap(repository::save)
                .map(this::toDto);
    }

    public Mono<ArticleDto> update(Long id, ArticleWriteDto dto) {
        return repository.findById(id)
                .flatMap(entity -> {
                    entity.setTitle(dto.title());
                    entity.setContent(dto.content());
                    return assignReferences(entity, dto.content());
                })
                .flatMap(repository::save)
                .map(this::toDto);
    }

    public Mono<Void> delete(Long id) {
        return repository.deleteById(id);
    }

    private Mono<ArticleEntity> assignReferences(ArticleEntity entity, String content) {
        Set<Long> ids = extractMentionIds(content);
        if (entity.getId() != null) {
            ids.remove(entity.getId());
        }
        if (ids.isEmpty()) {
            entity.setReferencedArticles(new HashSet<>());
            return Mono.just(entity);
        }
        return repository.findAllById(ids)
                .map(References::new)
                .collect(java.util.stream.Collectors.toCollection(HashSet::new))
                .map(refs -> {
                    entity.setReferencedArticles(refs);
                    return entity;
                });
    }

    private Set<Long> extractMentionIds(String content) {
        Set<Long> ids = new LinkedHashSet<>();
        if (content == null || content.isBlank()) {
            return ids;
        }
        try {
            JsonNode root = objectMapper.readTree(content);
            collectMentionIds(root, ids);
        } catch (Exception ignored) {
            // Content was not valid JSON; treat as plain text with no mentions.
        }
        return ids;
    }

    private void collectMentionIds(JsonNode node, Set<Long> ids) {
        if (node == null || node.isNull()) {
            return;
        }
        if (node.isArray()) {
            for (JsonNode child : node) {
                collectMentionIds(child, ids);
            }
            return;
        }
        if (node.isObject()) {
            JsonNode type = node.get("type");
            if (type != null && "mention".equals(type.asText())) {
                JsonNode targetId = node.get("targetArticleId");
                if (targetId != null && targetId.canConvertToLong()) {
                    ids.add(targetId.asLong());
                }
            }
            JsonNode children = node.get("children");
            if (children != null) {
                collectMentionIds(children, ids);
            }
        }
    }

    private ArticleDto toDto(ArticleEntity entity) {
        Set<References> refs = entity.getReferencedArticles();
        List<ArticleSummaryDto> refDtos = refs == null ? List.of() : refs.stream()
                .map(References::getTargetArticle)
                .filter(target -> target != null && target.getId() != null)
                .map(target -> new ArticleSummaryDto(target.getId(), target.getTitle()))
                .toList();
        return new ArticleDto(entity.getId(), entity.getTitle(), entity.getContent(), refDtos);
    }
}
