# -*- coding: utf8 -*-
from sanic import Sanic
from sanic.response import json
from common.proxy_loader import CachedProxies


PROXIES = None


def create_api_server(proxy_vendor_api, proxy_size):

    global PROXIES
    if PROXIES is None:
        PROXIES = CachedProxies(proxy_vendor_api, proxy_size=proxy_size)

    app = Sanic("ProxyAPIServer")

    @app.get("/proxy")
    async def get_proxy(request):
        return json({'data': PROXIES.get()})

    @app.post("/proxy/inactive")
    async def remove_proxy(request):
        proxy_info = request.json.get('data')
        proxy_info and PROXIES.remove(proxy_info)
        return json({'success': 0})

    return app