import requests
from fake_headers import Headers
from tqdm import tqdm

from .article_extractor import ArticleExtractor
from .article_filter import ArticleFilter
from ..fs_tools import get_absolute_path, make_dir, save_data_to_json


class HabrWebScraper:
    def __init__(self, kw, stream):
        self.domain: str = 'https://habr.com'
        self.keywords: list = kw
        self.response = None
        self.all_stream_urls = {
            'articles': '/ru/articles/',
            'posts': '/ru/posts/',
            'news': '/ru/news/',
            'feed': '/ru/feed/'
        }
        self.user_stream = stream

    def __str__(self):
        return (f'Url: {self.domain}\nKeywords: {self.keywords}\n'
                f'Response: {self.response}')

    def send_request(self):
        self.response = requests.get(
            f'{self.domain}{self.all_stream_urls[self.user_stream]}',
            headers=self._get_fake_headers()
        )

    def scrape(self):
        article_extractor = ArticleExtractor(self.response, self.domain)
        articles: list = article_extractor.get_articles()
        article_filter = ArticleFilter(self.keywords)

        return article_filter.filter_articles_by_keywords([
            article_extractor.extract_article_data(article)
            for article in tqdm(articles, desc='Filtering articles')
        ])

    @staticmethod
    def save_to_json_file(file_name, articles):
        with tqdm(desc='Saving articles to JSON file') as pbar:
            make_dir('habr_scraper_output')
            abs_path = get_absolute_path(['habr_scraper_output', file_name])
            save_data_to_json(articles, abs_path)
            pbar.update(1)

    @staticmethod
    def _get_fake_headers():
        return Headers(browser='chrome', os='windows').generate()
