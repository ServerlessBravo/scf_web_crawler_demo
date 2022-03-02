from queue import Empty
import threading
import logging
from web_crawler.index import main_handler
from common.message_queue import LocalQueue


local_queue = LocalQueue()


def consumer_thread_func():
    try:
        for apigw_event in iter(lambda: local_queue.get(), ''):
            sample_contxt = {
                'environment': '{"ENV": "dev", "LOG_LEVEL": "DEBUG", "PROXY_ENABLED": "True", "CHECK_PUBLIC_IP":"False", "PROXY_SERVER_BASE_URL":"http://127.0.0.1:9000"}', 
                'queue': local_queue}
            main_handler(apigw_event, sample_contxt)
    except Empty:
        logging.info("All messages has been processed, exiting application...")


sample_crawler_event = {
    "ResourceLink": "https://www.thriftbooks.com/browse/#b.s=bestsellers-desc&b.p=1&b.pp=50&b.nr",
    "TaskType": "VisitIndexPage",
    "Data": {
        "CurrentPageIndex": 1,
        "MaxPageIndex": 2
    }
}
local_queue.put(sample_crawler_event)

consumer_thead = threading.Thread(target=consumer_thread_func)
consumer_thead.start()

consumer_thead.join()
