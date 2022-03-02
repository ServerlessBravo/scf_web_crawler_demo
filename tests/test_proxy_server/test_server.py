import json, pytest, re
import httpretty
from proxy_server.server import create_api_server
from proxy_server.server import PROXIES as CACHED_PROXIES

PROXY_VENDOR_API="http://proxy.vendor.com/api"
PROXY_VENDOR_API_REGEXP=re.compile(r'http://proxy\.vendor\.com.*')
class TestForHappyPath:
    @pytest.fixture(scope='class')
    def setup_happy_path(self):
        httpretty.enable(verbose=True, allow_net_connect=True) 
        yield
        print("disable and resetting httpretty...")
        httpretty.disable() 
        httpretty.reset()

    @pytest.fixture(scope='class')
    def app(self):
        httpretty.register_uri(httpretty.GET, PROXY_VENDOR_API_REGEXP, body='{"code":0,"data":[{"ip":"1.1.1.1","port":2000,"expire_time":"2029-01-01 18:54:26"}],"msg":"0","success":true}')
        return create_api_server(PROXY_VENDOR_API, proxy_size=1)

    def test_should_send_api_requests_to_refresh_proxy(self, setup_happy_path, app ):
        CACHED_PROXIES = None
                
        _, response = app.test_client.get("/proxy")
        proxy_hash = json.loads(response.body)['data'][0]

        assert proxy_hash['http'] == "http://1.1.1.1:2000"
        assert proxy_hash['https'] == "http://1.1.1.1:2000"
        assert proxy_hash['expire_time'] == "2029-01-01 18:54:26"

        httpretty.disable() 
        httpretty.reset()

    def test_should_cache_proxy(self, setup_happy_path, app):
        CACHED_PROXIES = None
        _, response = app.test_client.get("/proxy")

        httpretty.reset()
        httpretty.register_uri(httpretty.GET, PROXY_VENDOR_API_REGEXP,
        body='{"code":0,"data":[{"ip":"2.2.2.2","port":2000,"expire_time":"2029-01-01 18:54:26"}],"msg":"0","success":true}')

        _, response = app.test_client.get("/proxy")
        proxy_hash = json.loads(response.body)['data'][0]

        assert proxy_hash['http'] == "http://1.1.1.1:2000"
        assert proxy_hash['https'] == "http://1.1.1.1:2000"
        assert proxy_hash['expire_time'] == "2029-01-01 18:54:26"

class TestForEdgeCases:

    @pytest.fixture(scope='class')
    def setup_edge_cases(self):
        httpretty.enable(verbose=True, allow_net_connect=True) 
        yield
        print("disable and resetting httpretty...")
        httpretty.disable() 
        httpretty.reset()

    number_of_api_calls = 0
    
    @pytest.fixture(scope='class')
    def reset_counter(self):
        TestForEdgeCases.number_of_api_calls = 0

    def test_should_refresh_if_cache_expired_proxy(self, setup_edge_cases, reset_counter):
        CACHED_PROXIES = None
        
        def bodyCallback(request, uri, headers):
            TestForEdgeCases.number_of_api_calls = TestForEdgeCases.number_of_api_calls + 1
            if TestForEdgeCases.number_of_api_calls == 1:
                return [200, {}, b'{"code":0,"data":[{"ip":"5.5.5.5","port":2000,"expire_time":"2021-01-01 18:54:26"}],"msg":"0","success":true}']
            else:
                return [200, {}, b'{"code":0,"data":[{"ip":"4.4.4.4","port":2000,"expire_time":"2029-01-01 18:54:26"}],"msg":"0","success":true}']

        httpretty.register_uri(httpretty.GET, PROXY_VENDOR_API_REGEXP , body=bodyCallback)

        app = create_api_server(PROXY_VENDOR_API, proxy_size=1)

        _, response = app.test_client.get("/proxy")
        proxy_hash = json.loads(response.body)['data'][0]

        assert proxy_hash['http'] == "http://4.4.4.4:2000"
        assert proxy_hash['https'] == "http://4.4.4.4:2000"
        assert proxy_hash['expire_time'] == "2029-01-01 18:54:26"