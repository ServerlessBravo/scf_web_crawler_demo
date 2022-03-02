
# -*- coding: utf8 -*-
from typing import Dict
from queue import Queue
import json

from common.http_client import CloudServiceHttpClient


class MessageQueue:
    def __init__(self) -> None:
        pass

    def put(self, msg: str) -> None:
        pass

    def get(self) -> str:
        pass


class LocalQueue(MessageQueue):
    def __init__(self) -> None:
        self.queue = Queue()

    def put(self, msg: Dict) -> None:
        apigw_event = json.dumps({
            'data': {
                'body': json.dumps(msg)
            }
        })
        self.queue.put(apigw_event)

    def get(self, timeout = 3) -> Dict:
        apigw_event = self.queue.get(block=False, timeout= timeout)
        return json.loads(apigw_event)


class EventBridge(MessageQueue):
    def __init__(self, webhook) -> None:
        self.webhook = webhook
        self.http_client = CloudServiceHttpClient()

    def put(self, msg: Dict) -> None:
        self.http_client.post(self.webhook, msg)

    def get(self) -> Dict:
        raise Exception("Should not be called on production environment")
