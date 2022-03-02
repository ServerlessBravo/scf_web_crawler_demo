import unittest
import json
from common.crawler_http_client import CrawlerHttpClient
from common.http_client import CloudServiceHttpClient

import httpretty
import requests
class TestHttpClient(unittest.TestCase):

    def tearDown(self) -> None:
        httpretty.disable()
        httpretty.reset()
        return super().tearDown()

    def test_should_send_requests(self):
        url = 'https://www.baidu.com/'
        http_client = CrawlerHttpClient()
        response = http_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_should_apply_response_hook_when_success(self):

        status_codes = []
        url = 'https://www.baidu.com/'

        def assert_status_hook(response, *args, **kwargs):
            status_codes.append(response.status_code)

        http_client = CrawlerHttpClient(response_hook=assert_status_hook)
        http_client.get(url)

        self.assertEqual(status_codes, [200])

    @httpretty.activate(verbose=True, allow_net_connect=False)
    def test_should_retry_3_times_by_default_with_bad_links(self):

        url = 'http://badlink.com'
        httpretty.register_uri(httpretty.GET, url, status=502)

        with self.assertRaises(requests.exceptions.RetryError):
            http_client = CrawlerHttpClient()
            http_client.get(url)
        
        number_of_requests = len(httpretty.latest_requests())
        self.assertEqual(number_of_requests, 4)
    
    @httpretty.activate(verbose=True, allow_net_connect=False)
    def test_should_retry_3_times_by_default_with_timeout(self):

        self.trigger_times = 0
        def bodyCallback(request, uri, headers):
            self.trigger_times = self.trigger_times + 1
            if( self.trigger_times != 4):
                raise requests.Timeout('Connection timed out.')
            else:
                return [200, {} , json.dumps({"hello": "world"})]


        url = 'http://timeoutlink.com'
        httpretty.register_uri(httpretty.GET, url, body=bodyCallback)

        http_client = CrawlerHttpClient()
        http_client.get(url)
    
        self.assertEqual(self.trigger_times, 4)

    @httpretty.activate(verbose=True, allow_net_connect=False)
    def test_should_cloud_service_http_client_retry_with_post_timeout(self):

        self.trigger_times = 0
        def bodyCallback(request, uri, headers):
            self.trigger_times = self.trigger_times + 1
            if( self.trigger_times != 4):
                raise requests.Timeout('Connection timed out.')
            else:
                return [200, {} , json.dumps({"hello": "world"})]


        url = 'http://fake_eb.com'
        httpretty.register_uri(httpretty.POST, url, body=bodyCallback)

        http_client = CloudServiceHttpClient()
        http_client.post(url, {'hello':'world'})
    
        self.assertEqual(self.trigger_times, 4)