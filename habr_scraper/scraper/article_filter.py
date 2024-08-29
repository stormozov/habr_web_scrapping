class ArticleFilter:
    """Filters articles based on keywords"""
    def __init__(self, keywords: list[str]) -> None:
        """Initializes the ArticleFilter class

        Args:
            keywords (list): List of keywords to filter by
        """
        self.keywords = keywords

    def filter_articles_by_keywords(self, articles: list[dict[str, str]]) \
            -> list[dict[str, str]]:
        """Filters articles based on keywords

        Args:
            articles (list[dict[str, str]]): List of articles to filter

        Returns:
            list[dict[str, str]]: List of filtered articles
        """
        if not self.keywords:
            return articles

        keywords_lower = [keyword.lower() for keyword in self.keywords]

        return [
            article
            for article in articles
            if self._article_matches_keywords(keywords_lower, article)
        ]

    @staticmethod
    def _article_matches_keywords(kw: list[str], article: dict[str, str]) \
            -> bool:
        """Checks if the article matches any of the keywords

        Args:
            kw (list[str]): List of keywords to check against
            article (dict[str, str]): The article to check

        Returns:
            bool: True if the article matches any of the keywords,
                False otherwise
        """
        article_data_lower: dict[str, str] = {
            'title': article['title'].lower(),
            'preview_text': article['preview_text'].lower(),
            'tags': [tag.lower() for tag in article['tags']]
        }
        return any(
            keyword in article_data_lower['title']
            or keyword in article_data_lower['preview_text']
            or keyword in article_data_lower['tags']
            for keyword in kw
        )
