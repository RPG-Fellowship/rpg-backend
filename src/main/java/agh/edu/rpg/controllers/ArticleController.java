package agh.edu.rpg.controllers;

import agh.edu.rpg.dto.ArticleDto;
import agh.edu.rpg.dto.ArticleSummaryDto;
import agh.edu.rpg.dto.ArticleWriteDto;
import agh.edu.rpg.services.ArticleService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/articles")
public class ArticleController {

    private final ArticleService service;

    public ArticleController(ArticleService service) {
        this.service = service;
    }

    @GetMapping
    public Flux<ArticleSummaryDto> list(@RequestParam(value = "q", required = false) String q) {
        return service.list(q);
    }

    @GetMapping("/{id}")
    public Mono<ResponseEntity<ArticleDto>> get(@PathVariable Long id) {
        return service.get(id)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build());
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Mono<ArticleDto> create(@RequestBody ArticleWriteDto body) {
        return service.create(body);
    }

    @PutMapping("/{id}")
    public Mono<ResponseEntity<ArticleDto>> update(@PathVariable Long id, @RequestBody ArticleWriteDto body) {
        return service.update(id, body)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public Mono<Void> delete(@PathVariable Long id) {
        return service.delete(id);
    }
}
