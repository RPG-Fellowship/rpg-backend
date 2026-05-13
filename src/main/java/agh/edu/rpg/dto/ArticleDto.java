package agh.edu.rpg.dto;

import java.util.List;

public record ArticleDto(Long id, String title, String content, List<ArticleSummaryDto> references) {
}
