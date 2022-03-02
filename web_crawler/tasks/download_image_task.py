# -*- coding: utf8 -*-
from typing import Dict
from common.soup_helpers import attr
from common.message_queue import Queue

class DownloadImageTask:
    def __init__(self, crawler_event: Dict, queue: Queue) -> None:
        self. queue = queue
        self.crawler_event = crawler_event
        self.page_link = self.crawler_event['ResourceLink']
        self.base_url = 'https://www.thriftbooks.com'

    
    def handle(self):
        print("Processing download img event", self.crawler_event)
        pass