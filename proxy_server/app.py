# -*- coding: utf8 -*-

import os
import sys

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.insert(1, vendor_dir)

## for import common module
common_dir = os.path.join(parent_dir, '..')
sys.path.insert(1, common_dir)

from proxy_server.server import create_api_server

## 通过环境变量注入 PROXY_VENDOR_API，用来批量获取Proxy列表

if __name__ == "__main__":
    proxy_vendor_api = os.environ.get('PROXY_VENDOR_API')
    if proxy_vendor_api is None:
        raise "Missing environment variable for PROXY_VENDOR_API"

    print("Vendor api is {}".format(proxy_vendor_api))
    api_server = create_api_server(proxy_vendor_api = proxy_vendor_api, proxy_size=100)
    api_server.run(host="0.0.0.0", port=9000, debug=True)