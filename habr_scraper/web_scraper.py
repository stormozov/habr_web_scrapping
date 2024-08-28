import bs4
import requests

from fake_headers import Headers
from habr_scraper.fs_tools import get_absolute_path, save_data_to_json, make_dir


class HabrWebScraper:
    def __init__(self, url, keywords, user_stream):
        self.domain: str = url
        self.keywords: list = keywords
        self.response = None
        self.all_stream_urls = {
            'articles': '/ru/articles/',
            'posts': '/ru/posts/',
            'news': '/ru/news/',
            'feed': '/ru/feed/'
        }
        self.user_stream = user_stream

    def __str__(self):
        return (f'Url: {self.domain}\nKeywords: {self.keywords}\n'
                f'Response: {self.response}')

    @staticmethod
    def _get_fake_headers():
        return Headers(browser='chrome', os='windows').generate()

    def send_request(self):
        self.response = requests.get(
            f'{self.domain}{self.all_stream_urls[self.user_stream]}',
            headers=self._get_fake_headers()
        )

    def get_articles(self):
        soup = bs4.BeautifulSoup(self.response.text, features='lxml')
        return soup.findAll('article', class_='tm-articles-list__item')

    @staticmethod
    def get_title(article):
        return article.find('h2', class_='tm-title_h2').text

    @staticmethod
    def get_datetime(article):
        return article.find('time')['datetime']

    def get_url(self, article):
        article_href = article.find('a', class_='tm-title__link')['href']
        return f'{self.domain}{article_href}'

    @staticmethod
    def get_preview_text(article):
        text_body = article.find('div', class_='article-formatted-body')
        html_tag_p = text_body.find_all('p')
        return ' '.join([el.text for el in html_tag_p])

    @staticmethod
    def get_author(article):
        return article.find('a', class_='tm-user-info__username').text

    @staticmethod
    def get_prev_img(article):
        img_element = article.find(
            'img', class_='tm-article-snippet__lead-image'
        )
        return img_element['src'] if img_element else None

    @staticmethod
    def get_tags(article):
        tags = (
            article
            .find_all('a', class_='tm-publication-hub__link')
        )
        return [el.text.replace('*', '') for el in tags]

    def extract_article_data(self, article) -> dict[str, str]:
        return {
            'title': self.get_title(article).strip(),
            'time': self.get_datetime(article),
            'url': self.get_url(article),
            'preview_text': self.get_preview_text(article).strip(),
            'author': self.get_author(article).strip(),
            'prev_img': self.get_prev_img(article),
            'tags': self.get_tags(article)
        }

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

    def filter_articles_by_keywords(self, articles: list) \
            -> list[dict[str, str]]:
        if not self.keywords:
            return [self.extract_article_data(article) for article in articles]

        keywords_lower = [keyword.lower() for keyword in self.keywords]

        return [
            self.extract_article_data(article)
            for article in articles
            if self._article_matches_keywords(
                keywords_lower, self.extract_article_data(article)
            )
        ]

    def scrape(self) -> list[dict[str, str]]:
        all_articles: list = self.get_articles()
        return self.filter_articles_by_keywords(all_articles)

    def get_articles_count(self) -> int:
        all_articles: list = self.scrape()
        return len(all_articles)

    def save_to_json_file(self, filename: str) -> None:
        make_dir('habr_scraper_output')
        abs_path = get_absolute_path(['habr_scraper_output', filename])
        save_data_to_json(self.scrape(), abs_path)


