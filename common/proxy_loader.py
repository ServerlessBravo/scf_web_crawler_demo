import json
import random
from time import sleep
import requests
from datetime import datetime, timedelta


MAX_RETRY_TIMES = 10
SLEEP_IN_SECONDS = 2
class CachedProxies:
    def __init__(self, proxy_vendor_api, proxy_size=50) -> None:
        self.proxy_loader = ProxyLoader(proxy_vendor_api, proxies_size=proxy_size)
        self.data = self.proxy_loader.load()
    
    def refresh(self):
        # safe under the mode of per request per instance
        print('begin to refresh proxies.....')
        self.data = self.proxy_loader.load()

    def remove(self, proxy):
        print("Trying to remove proxy:", proxy)
        ## memory is not shared across instances
        # self.refresh()

    def get(self) -> list:
        now = datetime.now()
        available_proxies = self.__available_proxies(now)

        if len(available_proxies) < 1:
            self.refresh()
            available_proxies = self.__available_proxies(now)

        return [random.choice(available_proxies)]

    def __available_proxies(self, now):
        future_time = now + timedelta(minutes=5)
        return list(filter(lambda p: datetime.fromisoformat(p['expire_time']) >= future_time, self.data))

class ProxyLoader:
    def __init__(self, proxy_vendor_api, proxies_size=1) -> None:
        self.proxy_vendor_api = proxy_vendor_api
        self.proxies_size = proxies_size

    def load(self) -> list:
        http_proxies = self.__get_random_http_proxies()
        return list(map(lambda p: self.__parse_result_to_proxy_hash(p) , http_proxies))
    
    def __parse_result_to_proxy_hash(self, p):
        proxy_url = "http://{0}:{1}".format(p['ip'], p['port'])
        return {"http": proxy_url, "https":proxy_url, "expire_time": p['expire_time']}


    def __get_random_http_proxies(self):
        results = [] 
        for _ in range(MAX_RETRY_TIMES):
            try:
                proxy_response = requests.get(self.proxy_vendor_api)
                print("---sending api requests-----", self.proxy_vendor_api)
                print(proxy_response.content)
                proxies = json.loads(proxy_response.content).get('data')
                if proxies and len(proxies) >= 1 and len(results) < self.proxies_size:
                    ## uniq 
                    results.extend(random.choices(proxies, k=self.proxies_size))
                    break
                else:
                    sleep(SLEEP_IN_SECONDS)

            except requests.exceptions.RequestException as err:
                print(err)
        return results