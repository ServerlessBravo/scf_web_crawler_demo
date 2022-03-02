# -*- coding: utf8 -*-

import os
import sys

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.insert(1, vendor_dir)

## for import common module
common_dir = os.path.join(parent_dir, '..')
sys.path.insert(1, common_dir)

import json

from .tasks.book_index_page_task import BookIndexPageTask
from .tasks.book_detail_page_task import BookDetailPageTask
from .tasks.download_image_task import DownloadImageTask

from common.message_queue import EventBridge

from requests import get


def main_handler(event, context):
    crawler_event = json.loads(event['data']['body'])
    print("crawler_event:", crawler_event)

    task_handler_dispatch(crawler_event, context)
    return("Hello World")


def task_handler_dispatch(crawler_event, context):
    env_str = context.get('environment') or '{"ENV": "dev", "LOG_LEVEL": "DEBUG", "PROXY_ENABLED": "False", "CHECK_PUBLIC_IP": "False"}'
    env_hash = json.loads(env_str)
    env_name = (env_hash.get('ENV') or 'dev').lower()
    proxy_enabled = (env_hash.get('PROXY_ENABLED') or 'False').upper() == 'TRUE'
    public_ip_check_enabled = (env_hash.get('CHECK_PUBLIC_IP') or 'False').upper() == 'TRUE'

    if public_ip_check_enabled:
        ip = get('https://api.ipify.org').text
        print(f'My public IP address is: {ip}')

    queue = None
    if env_name == 'prod':
        if 'EB_WEBHOOK' in env_hash:
            queue = EventBridge(env_hash['EB_WEBHOOK'])
        else:
            raise 'Missing webhook to send events to Event Bridge on prod environment!'
    else:
        print("Running under {0} environment....".format(env_name))
        queue = context.get('queue')

    app_config = {
        'proxy_enabled': proxy_enabled,
        'proxy_server_base_url': env_hash.get('PROXY_SERVER_BASE_URL') 
    }
    if crawler_event['TaskType'] == 'VisitIndexPage':
        BookIndexPageTask(crawler_event, queue, app_config).handle()

    if crawler_event['TaskType'] == 'VisitDetailPage':
        BookDetailPageTask(crawler_event, queue, app_config).handle()

    if crawler_event['TaskType'] == 'DownloadImage':
        DownloadImageTask(crawler_event, queue).handle()
