import requests
from fake_headers import Headers
from tqdm import tqdm

from .article_extractor import ArticleExtractor
from .article_filter import ArticleFilter
from ..fs_tools import get_absolute_path, make_dir, save_data_to_json


class HabrWebScraper:
    """Class for scrapping articles from habr"""
    def __init__(self, kw: list, stream: str) -> None:
        """Class for scrapping articles from habr

        Parameters:
            kw (list): List of keywords to search for.
            stream (str): Type of stream to scrape from.

        Attributes:
            domain (str): The base URL 'https://habr.com'.
            keywords (list): List of keywords provided.
            response: Response object from the HTTP request.
            all_stream_urls (dict): Dictionary mapping stream types to their
                respective URLs.
            user_stream (str): Type of stream chosen by the user.
        """
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

    def __str__(self) -> str:
        """Returns a string representation of the object"""
        return (f'Url: {self.domain}\nKeywords: {self.keywords}\n'
                f'Response: {self.response}')

    def send_request(self) -> None:
        """Sends an HTTP request to the specified URL"""
        self.response = requests.get(
            f'{self.domain}{self.all_stream_urls[self.user_stream]}',
            headers=self._get_fake_headers()
        )

    def scrape(self) -> list[dict[str, str]]:
        """Scrapes articles from the specified URL

        Returns:
            list: List of filtered articles based on keywords.
        """
        article_extractor = ArticleExtractor(self.response, self.domain)
        articles: list[dict[str, str]] = article_extractor.get_articles()
        article_filter = ArticleFilter(self.keywords)

        return article_filter.filter_articles_by_keywords([
            article_extractor.extract_article_data(article)
            for article in tqdm(articles, desc='Filtering articles')
        ])

    @staticmethod
    def save_to_json_file(file_name: str, articles: list[dict[str, str]]) \
            -> None:
        """Saves the list of articles to a JSON file.

        Args:
            file_name (str): The name of the file to save the data to.
            articles (list[dict[str, str]]): The list of articles to save.
        """
        with tqdm(desc='Saving articles to JSON file') as pbar:
            make_dir('habr_scraper_output')
            abs_path = get_absolute_path(['habr_scraper_output', file_name])
            save_data_to_json(articles, abs_path)
            pbar.update(1)

    @staticmethod
    def _get_fake_headers() -> dict[str, str]:
        """Returns a fake user agent header"""
        return Headers(browser='chrome', os='windows').generate()
