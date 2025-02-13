import time
import requests
from zapv2 import ZAPv2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

''' ====================== Website Information ====================== '''
scanning_url = 'https://www.saucedemo.com/inventory.html'
login_url = 'https://www.saucedemo.com/'
username = "standard_user"
password = "secret_sauce"

usrnm_varNAME = 'user-name'
passw_varNAME = 'password'

''' ====================== ZAP Configuration ====================== '''
zap_address = '127.0.0.1'
zap_port = 8080
apiKey = 'ui3c5012h6qqhen9ag0d1dmtlr'

''' ====================== Configure Selenium to use ZAP Proxy ====================== '''
proxy = f'{zap_address}:{zap_port}'
chrome_options = Options()
chrome_options.add_argument(f'--proxy-server=http://{proxy}')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-insecure-localhost')
chrome_options.add_argument('--disable-features=EnableEphemeralStorage')

driver = webdriver.Chrome(options=chrome_options)


''' ====================== Configure ZAP for Wider Coverage ====================== '''
def configure_zap(zap):
    headers = {
        'Accept': 'application/json',
        "X-ZAP-API-Key": apiKey
    }
    
    requests.get(f"http://{proxy}/JSON/core/action/setOptionHttpStateEnabled/", params={'Boolean': 'true'}, headers=headers)
    requests.get(f"http://{proxy}/JSON/ajaxSpider/action/setOptionClickDefaultElems/", params={'Boolean': 'true'}, headers=headers)
    requests.get(f"http://{proxy}/JSON/ajaxSpider/action/setOptionClickElemsOnce/", params={'Boolean': 'false'}, headers=headers)
    requests.get(f"http://{proxy}/JSON/ajaxSpider/action/setOptionEventWait/", params={'Integer': '3000'}, headers=headers)
    requests.get(f"http://{proxy}/JSON/ajaxSpider/action/setOptionReloadWait/", params={'Integer': '5000'}, headers=headers)
    requests.get(f"http://{proxy}/JSON/ajaxSpider/action/setOptionMaxDuration/", params={'Integer': '120'}, headers=headers)
    requests.get(f"http://{proxy}/JSON/ajaxSpider/action/setOptionMaxCrawlDepth/", params={'Integer': '10'}, headers=headers)
    zap.core.exclude_from_proxy("https://*.google.com")
    zap.core.exclude_from_proxy("https://*.facebook.com")
    zap.core.exclude_from_proxy("https://*.doubleclick.net")
    print("ZAP Configuration Completed")


def main():
    all_urls = set()
    
    try:
        print('Logging into the application...')
        driver.get(login_url)
        time.sleep(2)
        driver.find_element(By.NAME, usrnm_varNAME).send_keys(username)
        driver.find_element(By.NAME, passw_varNAME).send_keys(password)
        driver.find_element(By.NAME, passw_varNAME).send_keys(Keys.RETURN)
        time.sleep(5)
        print('Login completed')

        cookies = driver.get_cookies()
        cookie_value = "; ".join(f"{cookie['name']}={cookie['value']}" for cookie in cookies)
        
        zap = ZAPv2(apikey=apiKey, proxies={'http': f'http://{zap_address}:{zap_port}', 'https': f'http://{zap_address}:{zap_port}'})
        zap.replacer.add_rule(description="CookieHeader", enabled=True, matchtype="REQ_HEADER", matchregex=False, matchstring="Cookie", replacement=cookie_value)
        
        configure_zap(zap)
        
        print("Starting Classic Spider")
        requests.get(f"http://{proxy}/JSON/spider/action/scan/", params={'url': scanning_url}, headers={'X-ZAP-API-Key': apiKey})
        time.sleep(10)
        print("Classic Spider completed")

        spider_results = requests.get(f"http://{proxy}/JSON/spider/view/results/", headers={'X-ZAP-API-Key': apiKey}).json()
        found_urls = spider_results.get("results", [])
        all_urls.update(found_urls)
        print(f"Classic Spider found {len(found_urls)} URLs")
        
        print("Starting AJAX Spider")
        requests.get(f"http://{proxy}/JSON/ajaxSpider/action/scan/", params={'url': scanning_url}, headers={'X-ZAP-API-Key': apiKey})
        time.sleep(30)
        print("AJAX Spider completed")
        
        ajax_results = requests.get(f"http://{proxy}/JSON/ajaxSpider/view/fullResults/", headers={'X-ZAP-API-Key': apiKey}).json()
        ajax_urls = {entry["httprequest"].get("url") for entry in ajax_results.get("fullResults", []) if isinstance(entry, dict) and "httprequest" in entry}
        all_urls.update(ajax_urls)
        print(f"AJAX Spider found {len(ajax_urls)} URLs")

        print("Generating JSON Report")
        report_params = {'sites': scanning_url, 'reportFileName': "scan_report.json", 'title': f"{scanning_url} scanning report", 'template': "traditional-json"}
        requests.get(f"http://{proxy}/JSON/reports/action/generate/", params=report_params, headers={'X-ZAP-API-Key': apiKey})
        print("JSON report generation requested successfully")

    except Exception as e:
        print(f'An error occurred: {e}')

    finally:
        if all_urls:
            print(f"Total {len(all_urls)} discovered URLs written to url.txt")
            with open("url.txt", "w", encoding="utf-8") as f:
                for url in sorted(all_urls):
                    f.write(url + "\n")
        else:
            print("No URLs were discovered!")
        driver.quit()
        print("Script Complete")


if __name__ == "__main__":
    main()
