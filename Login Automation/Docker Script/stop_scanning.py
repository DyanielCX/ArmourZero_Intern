import requests
from zapv2 import ZAPv2


# ZAP Configuration (Change to your address, port & apiKey)
zap_address = '127.0.0.1'
zap_port = 8080
apiKey = 'ui3c5012h6qqhen9ag0d1dmtlr'


# Configure Selenium to use ZAP Proxy
proxy = f'{zap_address}:{zap_port}'

headers = {
    'Accept': 'application/json',
    "X-ZAP-API-Key": apiKey
}

requests.get(f"http://{proxy}/JSON/ajaxSpider/action/stop/", headers = headers)
requests.get(f"http://{proxy}/JSON/spider/action/stop/", headers = headers)
requests.get(f"http://{proxy}/JSON/ascan/action/removeAllScans/", headers = headers)



zap = ZAPv2(apikey=apiKey, proxies={
    'http': f'http://{zap_address}:{zap_port}',
    'https': f'http://{zap_address}:{zap_port}'
})

# Add custom header to ZAP proxy
# zap.replacer.remove_rule(description="RemoveCookieHeader")
