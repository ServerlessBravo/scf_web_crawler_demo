from urllib3.util.retry import Retry
from .http_client import HttpClient
from .http_client import CloudServiceHttpClient
import json
import requests

MAX_RETRY_TIMES_WHEN_PROXY_ERROR = 5

import http
# http.client.HTTPConnection.debuglevel = 1
class CrawlerHttpClient(HttpClient):
    def __init__(self, timeout=10, retry_strategy=None, response_hook=None, app_config=False) -> None:
        
        if retry_strategy is None:
            retry_strategy = Retry(connect=3, total=3,
                                   backoff_factor=0.3,
                                   status_forcelist=[301, 307, 429, 500, 502, 503, 504])
        http_headers = {
            'Connection': "close",
            'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        }

        proxies = None
        self.app_config = app_config
        self.cloud_service_client = CloudServiceHttpClient()
        self.proxy_enabled = self.app_config and self.app_config.get('proxy_enabled')

        if self.proxy_enabled:
            proxies = self.__load_proxies_from_remote()

        super().__init__(timeout=timeout, http_headers=http_headers,
                         retry_strategy=retry_strategy, hooks=dict(response=[response_hook]), proxies=proxies)



    def get(self, url):
        for _ in range(MAX_RETRY_TIMES_WHEN_PROXY_ERROR):
            try:
                return self._send(self._request(method='GET', url=url, headers=self.http_headers))
            except (
                    requests.exceptions.RequestException,
                    http.client.RemoteDisconnected,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.ProxyError) as err:

                if self.proxy_enabled:
                    print("Error with proxy: ", self.proxies)
                    print(err)
                    ## refresh proxy
                    print('inactive and refresh proxy due to proxy error...')
                    self.__remove_proxy_from_remote()
                    self.proxies = self.__load_proxies_from_remote()
                else:
                    raise err

    def __remove_proxy_from_remote(self):
        url = "{0}/proxy/inactive".format(self.app_config.get('proxy_server_base_url'))
        print("Removing proxy from remote", self.proxies)
        response = self.cloud_service_client.post(url, {'data': self.proxies})
        response.raise_for_status()

    def __load_proxies_from_remote(self):
        url = "{0}/proxy".format(self.app_config.get('proxy_server_base_url'))
        print("Loading proxies from remote ", url)
        content = self.cloud_service_client.get(url).content
        print('getting proxy data:', content)
        proxies = json.loads(content).get('data')[0]
        print("Proxy is enabled with:", proxies)
        return proxies