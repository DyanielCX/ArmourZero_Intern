import time
import requests
from zapv2 import ZAPv2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


''' Website Information '''
# Target URLs (Change to your own information)
scanning_url = 'https://juice-shop.herokuapp.com/profile'
login_url = 'https://juice-shop.herokuapp.com/#/login'
username = 'tester@gmail.com'
password = 'test123'


usrnm_varNAME = 'email'
passw_varNAME = 'password'

# ZAP Configuration (Change to your address, port & apiKey)
zap_address = '127.0.0.1'
zap_port = 8080
apiKey = 'ui3c5012h6qqhen9ag0d1dmtlr'


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
    time.sleep(2) 
    
    # Automate login
    driver.find_element(By.NAME, usrnm_varNAME).send_keys(username)
    driver.find_element(By.NAME, passw_varNAME).send_keys(password)
    driver.find_element(By.NAME, passw_varNAME).send_keys(Keys.RETURN)
    time.sleep(5)

    print('\nLogin completed!')

    ''' Section 2 '''
    # Retrieve and format the authentication session
    cookies = driver.get_cookies()

    # Set Header for API Request
    headers = {
        'Accept': 'application/json',
        "X-ZAP-API-Key": apiKey
    }

    # Prepare token value
    cookie_value = ""
    for cookie in cookies:
        cookie_value += f"{cookie['name']}={cookie['value']}; "

    zap = ZAPv2(apikey=apiKey, proxies={
        'http': f'http://{zap_address}:{zap_port}',
        'https': f'http://{zap_address}:{zap_port}'
    })

    # Add custom header to ZAP proxy
    zap.replacer.add_rule(
        description = "CookieHeader", 
        enabled = True, 
        matchtype = "REQ_HEADER", 
        matchregex = False, 
        matchstring = "Cookie", 
        replacement = cookie_value
    )


    ''' Section 3 '''
    # Spider
    params = {
        'url': scanning_url,
    }

    r = requests.get(f"http://{proxy}/JSON/spider/action/scan/", params=params, headers = headers)

    while True:
        time.sleep(5)
        progress = requests.get(f"http://{proxy}/JSON/spider/view/status/", headers = headers).json()
        print(f"Scan Progress: {progress['status']}%")

        if progress["status"] == "100":
            result = requests.get(f"http://{proxy}/JSON/spider/view/results/", headers = headers).json()
            print(result)
            break

    # requests.get(f"http://{proxy}/JSON/spider/action/stop/", headers = headers)
        

    # Ajax Spider
    params = {
        'url': scanning_url,
    }
    
    r = requests.get(f"http://{proxy}/JSON/ajaxSpider/action/setOptionClickDefaultElems/", params={
        'Boolean': 'true'
    }, headers = headers)

    r = requests.get(f"http://{proxy}/JSON/ajaxSpider/action/scan/", params=params, headers = headers)

    while True:
        time.sleep(15)
        progress = requests.get(f"http://{proxy}/JSON/ajaxSpider/view/status/", headers = headers).json()
        print(f"Scan Status: {progress['status']}")

        if progress["status"] == "stopped":
            result = requests.get(f"http://{proxy}/JSON/ajaxSpider/view/fullResults/", headers = headers).json()
            print(result)
            break

    # # requests.get(f"http://{proxy}/JSON/ajaxSpider/action/stop/", headers = headers)


    # Active Scan
    scan_data = {
        "url": scanning_url,
        "recurse": "true",
        "apikey": apiKey,
    }
    response = requests.post(f"http://{proxy}/JSON/ascan/action/scan/", headers=headers, data=scan_data)

    scan_id = response.json()["scan"]
    while True:
        time.sleep(15)
        progress = requests.get(f"http://{proxy}/JSON/ascan/view/status/?scanId={scan_id}", headers=headers).json()
        print(f"Scan Progress: {progress['status']}%")

        if progress["status"] == "100":
            break

    # requests.get(f"http://{proxy}/JSON/ascan/action/removeAllScans/", headers = headers)


    # Generate JSON report
    json_report = requests.get(f"http://{proxy}/JSON/reports/action/generate/", params={
            'sites' : scanning_url,
            'reportFileName': "scan_report.json",
            'title': f"{scanning_url} scanning report",
            'template': "traditional-json"
        }, headers=headers)

except Exception as e:
    print(f'An error occurred: {e}')

finally:
    # Close the Selenium WebDriver
    driver.quit()