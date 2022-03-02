# -*- coding: utf8 -*-
import json
import requests
import urllib3
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


import requests
from urllib3.exceptions import InsecureRequestWarning
# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class HttpClient:
    def __init__(self, timeout=3, http_headers=None, retry_strategy=None, hooks=None, proxies=None) -> None:
        self.session = requests.Session()
        self.http_headers = http_headers
        self.timeout = timeout
        self.proxies = proxies
        if hooks:
            self.session.hooks.update(hooks)

        if retry_strategy:
            self.session.mount(
                'http://', HTTPAdapter(max_retries=retry_strategy))
            self.session.mount(
                'https://', HTTPAdapter(max_retries=retry_strategy))

    def get(self, url):
        return self._send(self._request(method='GET', url=url, headers=self.http_headers))

    def post(self, url, obj):
        request = self._request(method='POST', url=url, data=json.dumps(obj), headers={
            'Content-Type': 'application/json'
        })
        return self._send(request)

    def _send(self, prepared_request):
        try:
            resp = self.session.send(prepared_request, allow_redirects=False, timeout=self.timeout, proxies=self.proxies, verify=False)
            return resp
        except urllib3.exceptions.MaxRetryError as err:
            print('Error happend with url:', prepared_request.url)
            raise err

    def _request(self, method, url, data=None, headers=None):
        r = requests.Request(
            method=method,
            url=url,
            data=data,
            headers=headers)
        return self.session.prepare_request(r)

    def __del__(self):
        if self.session:
            self.session.close()


class CloudServiceHttpClient(HttpClient):
    def __init__(self, headers = None) -> None:
        retry_strategy = Retry(connect=3, 
                               allowed_methods=frozenset(['GET', 'POST']),
                               total=3,
                               backoff_factor=0.7,
                               status_forcelist=[429, 502, 503, 504],
                               )
        super().__init__(timeout=5, retry_strategy=retry_strategy, http_headers = headers)