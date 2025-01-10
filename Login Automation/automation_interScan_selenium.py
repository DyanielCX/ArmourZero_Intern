#!/usr/bin/env python
import os
import time
from pprint import pprint
from zapv2 import ZAPv2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

''' Launch OWASP ZAP '''
path = "D:/Program Files/ZAP/Zed Attack Proxy/"
os.chdir(path)
os.system("ZAP.exe")
time.sleep(20)

''' Website Information '''
# Target URLs
scanning_url = 'https://webapp3.wimify.xyz/profile'
login_url = 'https://webapp3.wimify.xyz/#/login'
username = 'tester@gmail.com'
password = 'test123'
usrnm_varNAME = 'email'
passw_varNAME = 'password'

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
    ''' Section 1 '''
    # Log in to the application using Selenium
    print('--- Account Login ---')
    print('Logging into the application...')
    driver.get(login_url)
    time.sleep(2)  # Wait for the page to load
    
    # Automate login
    driver.find_element(By.NAME, usrnm_varNAME).send_keys(username)
    driver.find_element(By.NAME, passw_varNAME).send_keys(password)
    driver.find_element(By.NAME, passw_varNAME).send_keys(Keys.RETURN)
    time.sleep(5)
    
    print('Login completed!')
    print('')


    ''' Section 2 '''
    # Scanning target with ZAP
    
    ## ZAP Spider ##
    print('--- ZAP Spider ---')
    print('Starting ZAP spidering...')
    scanID = zap.spider.scan(scanning_url)
    while int(zap.spider.status(scanID)) < 100:
        # Poll the status until it completes
        print('Spider progress %: {}'.format(zap.spider.status(scanID)))
        time.sleep(1)

    print('Spider has completed!')
    # Print the URLs crawled by the spider
    print('\n'.join(map(str, zap.spider.results(scanID))))
    print('')

    
    ## ZAP Ajax Spider ##
    print('--- ZAP Ajax Spider ---')
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
    print('')


    ## ZAP Active Scan ##
    print('--- ZAP Active Scan ---')
    print('Active Scanning target {}'.format(scanning_url))
    scanID = zap.ascan.scan(scanning_url)
    while int(zap.ascan.status(scanID)) < 100:
        # Loop until the scanner has finished
        print('Scan progress %: {}'.format(zap.ascan.status(scanID)))
        time.sleep(5)

    print('Active Scan completed')
    print('')
    # Print vulnerabilities found by the scanning
    print('Hosts: {}'.format(', '.join(zap.core.hosts)))
    print('Alerts: ')
    pprint(zap.core.alerts(baseurl=scanning_url))

except Exception as e:
    print(f'An error occurred: {e}')

finally:
    # Close the Selenium WebDriver
    driver.quit()
