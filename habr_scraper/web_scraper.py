import bs4
import requests

from fake_headers import Headers


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

    def filter_articles_by_keywords(self, articles: list):
        filtered_articles = []

        for article in articles:
            article_title = self.get_title(article).strip()
            article_preview_text = self.get_preview_text(article).strip()
            article_author = self.get_author(article).strip()
            article_datatime = self.get_datetime(article)
            article_url = self.get_url(article)
            article_prev_img = self.get_prev_img(article)
            article_tag = self.get_tags(article)

            if any(keyword.lower() in article_title.lower()
                   or keyword.lower() in article_preview_text.lower()
                   or keyword.lower() in [tag.lower() for tag in article_tag]
                   for keyword in self.keywords):
                filtered_articles.append({
                    'title': article_title,
                    'time': article_datatime,
                    'url': article_url,
                    'preview_text': article_preview_text,
                    'author': article_author,
                    'prev_img': article_prev_img,
                    'tags': article_tag
                })

        yield from filtered_articles

    def scrape(self):
        all_articles: list = self.get_articles()
        filtered_articles = self.filter_articles_by_keywords(all_articles)

        return filtered_articles

