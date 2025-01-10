#!/usr/bin/env python
import time
from zapv2 import ZAPv2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

''' Website Information '''
# Target URLs
scanning_url = 'http://localhost/SHARK/'
login_url = 'http://localhost/SHARK/'
username = 'tester@gmail.com'
password = 'test123'
usrnm_varNAME = 'login_email'
passw_varNAME = 'login_pwsd'

# ZAP Configuration
zap_address = '127.0.0.1'
zap_port = 8080
apiKey = 'ui3c5012h6qqhen9ag0d1dmtlr'
zap = ZAPv2(apikey=apiKey, proxies={
    'http': f'http://{zap_address}:{zap_port}',
    'https': f'http://{zap_address}:{zap_port}'
})

# Configure Selenium to use ZAP Proxy
proxy = f'{zap_address}:{zap_port}'
chrome_options = Options()
chrome_options.add_argument(f'--proxy-server=http://{proxy}')
chrome_options.add_argument('--ignore-certificate-errors') 
chrome_options.add_argument('--allow-insecure-localhost')

# Launch Selenium WebDriver with ZAP proxy
driver = webdriver.Chrome(options=chrome_options)

try:
    # Step 1: Log in to the application using Selenium
    print('Logging into the application...')
    driver.get(login_url)
    time.sleep(2)  # Wait for the page to load
    
    # Automate login
    driver.find_element(By.NAME, usrnm_varNAME).send_keys(username)
    driver.find_element(By.NAME, passw_varNAME).send_keys(password)
    driver.find_element(By.NAME, passw_varNAME).send_keys(Keys.RETURN)
    time.sleep(5)
    
    print('Login completed!')

    # Step 2: Scanning target with ZAP

    ## ZAP Spider ##
    print('Starting ZAP spidering...')
    scanID = zap.spider.scan(scanning_url)
    while int(zap.spider.status(scanID)) < 100:
        # Poll the status until it completes
        print('Spider progress %: {}'.format(zap.spider.status(scanID)))
        time.sleep(1)

    print('Spider has completed!')
    # Print the URLs crawled by the spider
    print('\n'.join(map(str, zap.spider.results(scanID))))

    ## ZAP Ajax Spider ##
    print('Ajax Spider target {}'.format(scanning_url))
    scanID = zap.ajaxSpider.scan(scanning_url)

    timeout = time.time() + 60*2   # 2 minutes from now
    # Loop until the ajax spider has finished or the timeout has exceeded
    while zap.ajaxSpider.status == 'running':
        if time.time() > timeout:
            break
        print('Ajax Spider status' + zap.ajaxSpider.status)
        time.sleep(2)

    print('Ajax Spider completed')
    ajaxResults = zap.ajaxSpider.results(start=0, count=10)

except Exception as e:
    print(f'An error occurred: {e}')

finally:
    # Close the Selenium WebDriver
    driver.quit()
