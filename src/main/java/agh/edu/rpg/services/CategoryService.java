package agh.edu.rpg.services;

import agh.edu.rpg.repositories.CategoryRepository;
import org.springframework.stereotype.Service;
import tools.jackson.databind.ObjectMapper;

@Service
public class CategoryService {
    private final CategoryRepository categoryRepository;
    private final ObjectMapper objectMapper;


    public CategoryService(CategoryRepository categoryRepository, ObjectMapper objectMapper) {
        this.categoryRepository = categoryRepository;
        this.objectMapper = objectMapper;
    }



}
