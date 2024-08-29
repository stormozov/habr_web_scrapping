import requests

from bs4 import BeautifulSoup
from tqdm import tqdm


class ArticleExtractor:
    def __init__(self, response, domain):
        self.response = response
        self.domain = domain
        self.soup = BeautifulSoup(self.response.text, features='lxml')

    def get_articles(self):
        with tqdm(desc='Scraping articles') as pbar:
            pbar.update(1)
            return self.soup.findAll('article', class_='tm-articles-list__item')

    def extract_article_data(self, article):
        return {
            'title': self.extract_title(article).strip(),
            'time': self.extract_datetime(article),
            'url': self.extract_url(article),
            'preview_text': self.extract_preview_text(article).strip(),
            'full_text': self.extract_full_text(article).strip(),
            'author': self.extract_author(article).strip(),
            'prev_img': self.extract_prev_img(article),
            'tags': self.extract_tags(article)
        }

    def extract_title(self, article):
        return self._find_element(article, 'h2', 'tm-title_h2').text

    def extract_datetime(self, article):
        return self._find_element(article, 'time')['datetime']

    def extract_url(self, article):
        article_href = self._find_element(
            article, 'a', 'tm-title__link')['href']
        return f'{self.domain}{article_href}'

    def extract_preview_text(self, article):
        text_body = self._find_element(
            article, 'div', 'article-formatted-body')
        html_tag_p = self._find_element(text_body, 'p', multiple=True)
        return ' '.join([el.text for el in html_tag_p])

    def extract_full_text(self, article):
        url = self.extract_url(article)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features='lxml')
        article_text = self._find_element(
            soup, 'div', 'article-formatted-body')
        return article_text.text

    def extract_author(self, article):
        return self._find_element(
            article, 'a', 'tm-user-info__username').text

    def extract_prev_img(self, article):
        img_element = self._find_element(
            article, 'img', 'tm-article-snippet__lead-image')
        return img_element['src'] if img_element else None

    def extract_tags(self, article):
        tags = self._find_element(
            article, 'a',
            'tm-publication-hub__link', True
        )
        return [el.text.replace('*', '') for el in tags]

    @staticmethod
    def _find_element(article, tag, class_=None, multiple=False):
        if multiple:
            return article.find_all(tag, class_=class_)
        else:
            return article.find(tag, class_=class_)
