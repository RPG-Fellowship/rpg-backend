class ArticleNotFoundException(Exception):
    def __str__(self):
        return "Could not find article with the given ID"