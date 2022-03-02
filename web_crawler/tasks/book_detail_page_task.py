from datetime import datetime
from typing import Dict
from bs4 import BeautifulSoup
from common.crawler_http_client import CrawlerHttpClient
from common.soup_helpers import text, attr
from common.message_queue import Queue


class BookDetailPageTask:
    def __init__(self, crawler_event: Dict, queue: Queue, app_config) -> None:
        self. queue = queue
        self.crawler_event = crawler_event
        self.page_link = self.crawler_event['ResourceLink']
        self.http_client = CrawlerHttpClient(app_config=app_config)

    def handle(self):
        content = self.http_client.get(self.page_link).content
        soup = BeautifulSoup(content, "html.parser")
        detail_doc = soup.find('div', id='Work-desktop')
        if detail_doc:
            result = self.__parse_book_detail_info(detail_doc)

            self.__persistence_book_detail_info(result)

            result.get('Url') and self.queue.put({
                "ResourceLink": result.get('Img_url'),
                "TaskType": "DownloadImage",
                "Data": {
                    "ISBN": result.get('ISBN')
                }
            })

    def __persistence_book_detail_info(self, result):
        # sample code for persistence
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print('CurrentTime:', current_time, result)

    def __parse_book_detail_info(self, doc):
        isbns_doc = doc.find('div', class_='WorkCoverSidebar-isbns')
        isbn_doc = isbns_doc.find('span', class_='WorkSelector-bold')

        title_doc = doc.find(
            'h1', class_='WorkMeta-title Alternative Alternative-title')
        author_doc = doc.find('div', class_='WorkMeta-authors').find('a')
        desc_doc = doc.find('p', class_='WorkMeta-overview').find('span')

        rating_container_doc = doc.find(
            'div', class_='WorkMeta-ratingContainer')
        rating_doc = rating_container_doc.find(
            'meta', attrs={'itemprop': 'ratingValue'})
        review_doc = rating_container_doc.find(
            'meta', attrs={'itemprop': 'reviewCount'})

        img_cover_doc = doc.find('div', class_="WorkCover").find('img')

        price_doc = doc.find('div', class_='WorkSelector-price')

        return {
            'ISBN': text(isbn_doc),
            'Title': text(title_doc),
            'Description': text(desc_doc),
            'Author': text(author_doc),
            'Price': text(price_doc),
            'Rating': attr(rating_doc, 'content'),
            'Review': attr(review_doc, 'content'),
            'Img_url': attr(img_cover_doc, 'src'),
            'Img_alt': attr(img_cover_doc, 'alt'),
            'Url': self.page_link
        }
