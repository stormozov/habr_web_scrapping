class ArticleFilter:
    def __init__(self, keywords):
        self.keywords = keywords

    def filter_articles_by_keywords(self, articles):
        if not self.keywords:
            return articles

        keywords_lower = [keyword.lower() for keyword in self.keywords]

        return [
            article
            for article in articles
            if self._article_matches_keywords(keywords_lower, article)
        ]

    @staticmethod
    def _article_matches_keywords(kw, article):
        article_data_lower = {
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
