from habr_scraper import HabrWebScraper

if __name__ == '__main__':
    DOMAIN = 'https://habr.com'
    KEYWORDS = ['дизайн', 'фото', 'web', 'python']
    scraper = HabrWebScraper(DOMAIN, KEYWORDS, 'articles')
    scraper.send_request()
    result = scraper.scrape()
