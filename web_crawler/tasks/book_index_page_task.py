# -*- coding: utf8 -*-
from typing import Dict
from bs4 import BeautifulSoup
from common.soup_helpers import attr
from common.crawler_http_client import CrawlerHttpClient
from common.message_queue import Queue


class BookIndexPageTask:

    def __init__(self, crawler_event: Dict, queue: Queue, app_config) -> None:
        self. queue = queue
        self.crawler_event = crawler_event
        self.page_link = self.crawler_event['ResourceLink']
        self.base_url = 'https://www.thriftbooks.com'
        self.http_client = CrawlerHttpClient(app_config = app_config)
        self.extra_data = self.crawler_event.get('Data')

    def handle(self):
        ## Send the event for next page at first to avoid program stopped due to proxy error
        self.__send_link_for_next_index_page()

        content = self.http_client.get(self.page_link).content
        soup = BeautifulSoup(content, "html.parser")
        results = soup.find_all('a', class_="SearchResultGridItem")
        for result in results:
            detail_relative_link = attr(result, 'href')
            detail_relative_link and self.queue.put({
                "ResourceLink": detail_relative_link and (self.base_url + detail_relative_link),
                "TaskType": "VisitDetailPage",
                "Data": self.extra_data
            })

    def __send_link_for_next_index_page(self):
        current_page_index = int(self.extra_data['CurrentPageIndex'])
        max_page_index = int(self.extra_data['MaxPageIndex'])

        if current_page_index + 1 <= max_page_index:
            # https://www.thriftbooks.com/browse/#b.s=bestsellers-desc&b.p=199&b.pp=50&b.nr
            next_index_page = self.page_link.replace("b.p={0}".format(
                current_page_index), "b.p={0}".format(current_page_index + 1))
            self.queue.put({
                "ResourceLink": next_index_page,
                "TaskType": "VisitIndexPage",
                "Data": {
                    "CurrentPageIndex": current_page_index + 1,
                    "MaxPageIndex": max_page_index
                }}
            )