import bs4
import requests

from fake_headers import Headers
from habr_scraper.fs_tools import get_absolute_path, save_data_to_json, make_dir
from tqdm import tqdm


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

    def get_articles(self):
        soup = bs4.BeautifulSoup(self.response.text, features='lxml')
        return soup.findAll('article', class_='tm-articles-list__item')

    def get_title(self, article):
        return self._find_element(article, 'h2', 'tm-title_h2').text

    def get_datetime(self, article):
        return self._find_element(article, 'time')['datetime']

    def get_url(self, article):
        article_href = self._find_element(
            article, 'a', 'tm-title__link')['href']
        return f'{self.domain}{article_href}'

    def get_preview_text(self, article):
        text_body = self._find_element(
            article, 'div', 'article-formatted-body')
        html_tag_p = self._find_element(text_body, 'p', multiple=True)
        return ' '.join([el.text for el in html_tag_p])

    def get_full_article_text(self, url):
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, features='lxml')
        article_text = self._find_element(
            soup, 'div', 'article-formatted-body')
        return article_text.text

    def get_author(self, article):
        return self._find_element(
            article, 'a', 'tm-user-info__username').text

    def get_prev_img(self, article):
        img_element = self._find_element(
            article, 'img', 'tm-article-snippet__lead-image')
        return img_element['src'] if img_element else None

    def get_tags(self, article):
        tags = self._find_element(
            article, 'a',
            'tm-publication-hub__link', True
        )
        return [el.text.replace('*', '') for el in tags]

    def filter_articles_by_keywords(self, articles: list[dict[str, str]]) \
            -> list[dict[str, str]]:
        if not self.keywords:
            return [self._extract_article_data(article) for article in articles]

        keywords_lower = [keyword.lower() for keyword in self.keywords]

        return [
            self._extract_article_data(article)
            for article in tqdm(articles, desc='Filtering articles')
            if self._article_matches_keywords(
                keywords_lower, self._extract_article_data(article)
            )
        ]

    def scrape(self) -> list[dict[str, str]]:
        with tqdm(desc='Scraping articles') as pbar:
            all_articles: list = self.get_articles()
            pbar.update(1)
        return self.filter_articles_by_keywords(all_articles)

    @staticmethod
    def get_articles_count(articles: list[dict[str, str]]) -> int:
        return len(articles)

    @staticmethod
    def save_to_json_file(file_name: str, articles: list[dict[str, str]]) \
            -> None:
        with tqdm(desc='Saving articles to JSON file') as pbar:
            make_dir('habr_scraper_output')
            abs_path = get_absolute_path(['habr_scraper_output', file_name])
            save_data_to_json(articles, abs_path)
            pbar.update(1)

    @staticmethod
    def _get_fake_headers():
        return Headers(browser='chrome', os='windows').generate()

    @staticmethod
    def _find_element(
            article: bs4.element, tag: str,
            class_: str = None, multiple: bool = False
    ):
        if multiple:
            return article.find_all(tag, class_=class_)
        else:
            return article.find(tag, class_=class_)

    @staticmethod
    def _article_matches_keywords(keywords: list, article: dict[str, str]) \
            -> bool:
        article_data_lower = {
            'title': article['title'].lower(),
            'preview_text': article['preview_text'].lower(),
            'tags': [tag.lower() for tag in article['tags']]
        }
        return any(
            keyword in article_data_lower['title']
            or keyword in article_data_lower['preview_text']
            or keyword in article_data_lower['tags']
            for keyword in keywords
        )

    def _extract_article_data(self, article) -> dict[str, str]:
        return {
            'title': self.get_title(article).strip(),
            'time': self.get_datetime(article),
            'url': self.get_url(article),
            'preview_text': self.get_preview_text(article).strip(),
            'full_text': self.get_full_article_text(self.get_url(article)),
            'author': self.get_author(article).strip(),
            'prev_img': self.get_prev_img(article),
            'tags': self.get_tags(article)
        }
