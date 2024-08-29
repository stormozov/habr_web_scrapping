import requests

from bs4 import BeautifulSoup
from tqdm import tqdm


class ArticleExtractor:
    """Class for extracting article data from HTML response"""
    def __init__(self, response: requests.Response, domain: str) -> None:
        """Initialize the ArticleExtractor object.

        Args:
            response: The response object from the HTTP request.
            domain: The domain of the website.
        """
        self.response = response
        self.domain = domain
        self.soup = BeautifulSoup(self.response.text, features='lxml')

    def get_articles(self) -> list[dict[str, str]]:
        """Get articles from the HTML response.

        Returns:
            list[dict[str, str]]: A list of article data dictionaries.
        """
        with tqdm(desc='Scraping articles') as pbar:
            pbar.update(1)
            return self.soup.findAll('article', class_='tm-articles-list__item')

    def extract_article_data(self, article: BeautifulSoup) -> dict[str, str]:
        """Extract article data from the HTML article element.

        Args:
            article: The HTML article element.

        Returns:
            dict[str, str]: A dictionary of article data.
        """
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

    def extract_title(self, article: BeautifulSoup) -> str:
        """Extract the article title from the HTML article element.

        Args:
            article: The HTML article element.

        Returns:
            str: The article title.
        """
        return self._find_element(article, 'h2', 'tm-title_h2').text

    def extract_datetime(self, article: BeautifulSoup) -> str:
        """Extract the article datetime from the HTML article element.

        Args:
            article: The HTML article element.

        Returns:
            str: The article datetime.
        """
        return self._find_element(article, 'time')['datetime']

    def extract_url(self, article: BeautifulSoup) -> str:
        """Extract the article URL from the HTML article element.

        Args:
            article: The HTML article element.

        Returns:
            str: The article URL.
        """
        article_href = self._find_element(
            article, 'a', 'tm-title__link')['href']
        return f'{self.domain}{article_href}'

    def extract_preview_text(self, article: BeautifulSoup) -> str:
        """Extract the article preview text from the HTML article element.

        Args:
            article: The HTML article element.

        Returns:
            str: The article preview text.
        """
        text_body = self._find_element(
            article, 'div', 'article-formatted-body')
        html_tag_p = self._find_element(text_body, 'p', multiple=True)
        return ' '.join([el.text for el in html_tag_p])

    def extract_full_text(self, article: BeautifulSoup) -> str:
        """Extract the article full text from the HTML article element.

        Args:
            article: The HTML article element.

        Returns:
            str: The article full text.
        """
        url = self.extract_url(article)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features='lxml')
        article_text = self._find_element(
            soup, 'div', 'article-formatted-body')
        return article_text.text

    def extract_author(self, article: BeautifulSoup) -> str:
        """Extract the article author from the HTML article element.

        Args:
            article: The HTML article element.

        Returns:
            str: The article author.
        """
        return self._find_element(
            article, 'a', 'tm-user-info__username').text

    def extract_prev_img(self, article: BeautifulSoup) -> str:
        """Extract the article preview image from the HTML article element.

        Args:
            article: The HTML article element.

        Returns:
            str: Link to article preview
        """
        img_element = self._find_element(
            article, 'img', 'tm-article-snippet__lead-image')
        return img_element['src'] if img_element else None

    def extract_tags(self, article: BeautifulSoup) -> list[str]:
        """Extract the article tags from the HTML article element.

        Args:
            article: The HTML article element.

        Returns:
            list[str]: The article tags.
        """
        tags = self._find_element(
            article, 'a',
            'tm-publication-hub__link', True
        )
        return [el.text.replace('*', '') for el in tags]

    @staticmethod
    def _find_element(
        article: BeautifulSoup,
        tag: str,
        class_: str = None,
        multiple: bool = False
    ) -> BeautifulSoup | list[BeautifulSoup]:
        """Find an element in the HTML article element.

        Args:
            article: The article as a BeautifulSoup object.
            tag: The tag to search for.
            class_: The class to search for. Defaults to None.
            multiple: Whether to return multiple elements. Defaults to False.

        Returns:
            If multiple is False, a BeautifulSoup element is returned.
            If multiple is True, a list of BeautifulSoup elements is returned.
        """
        if multiple:
            return article.find_all(tag, class_=class_)
        else:
            return article.find(tag, class_=class_)
