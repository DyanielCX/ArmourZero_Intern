#!/usr/bin/env python
import time
import json
from zapv2 import ZAPv2

# The URL of the application to be tested
target = 'https://webapp9.wimify.xyz/profile/aztest'
# Change to match the API key set in ZAP, or use None if the API key is disabled
apiKey = 'ui3c5012h6qqhen9ag0d1dmtlr'

# By default ZAP API client will connect to port 8080
zap = ZAPv2(apikey=apiKey)
# Use the line below if ZAP is not listening on port 8080, for example, if listening on port 8090
# zap = ZAPv2(apikey=apiKey, proxies={'http': 'http://127.0.0.1:8090', 'https': 'http://127.0.0.1:8090'})

print('Ajax Spider target {}'.format(target))
scanID = zap.ajaxSpider.scan(target)

timeout = time.time() + 60*2   # 2 minutes from now
# Loop until the ajax spider has finished or the timeout has exceeded
while zap.ajaxSpider.status == 'running':
    if time.time() > timeout:
        break
    print('Ajax Spider status' + zap.ajaxSpider.status)
    time.sleep(2)

print('Ajax Spider completed')
ajaxResults = zap.ajaxSpider.full_results

print("\nAjax Spider Results:")
# Process only inScope results
for result in ajaxResults.get("inScope", []):
    print(json.dumps(result))

# If required perform additional operations with the Ajax Spider results

# TODO: Start scanning the application to find vulnerabilities