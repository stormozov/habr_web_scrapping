from habr_scraper.scraper import HabrWebScraper

if __name__ == '__main__':
    KEYWORDS = ['дизайн', 'фото', 'web', 'python']
    scraper = HabrWebScraper(KEYWORDS, 'articles')
    scraper.send_request()
    articles: list[dict[str, str]] = scraper.scrape()
    scraper.save_to_json_file('habr', articles)

    print(scraper.get_scrape_info(articles))
