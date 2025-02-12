import time
import requests
from zapv2 import ZAPv2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

''' ====================== Website Information ====================== '''
scanning_url = 'https://webapp8.wimify.xyz/home'
login_url = 'https://webapp8.wimify.xyz/login#login'
username = 'mvpchen2@gmail.com'
password = 'Password123'

usrnm_varNAME = 'email'
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

driver = webdriver.Chrome(options=chrome_options)

def main():
    all_urls = set()  # We'll store every discovered URL here, then write them to a file at the end

    try:
        ''' ====================== SECTION 1: Login via Selenium ====================== '''
        print('--- Account Login ---')
        print('Logging into the application...')
        driver.get(login_url)
        time.sleep(2)  # Wait for the login page to load

        # Automate login
        driver.find_element(By.NAME, usrnm_varNAME).send_keys(username)
        driver.find_element(By.NAME, passw_varNAME).send_keys(password)
        driver.find_element(By.NAME, passw_varNAME).send_keys(Keys.RETURN)
        time.sleep(5)

        print('\nLogin completed!')

        ''' ====================== SECTION 2: Configure ZAP & Replacer for Cookies ====================== '''
        cookies = driver.get_cookies()

        cookie_value = ""
        for cookie in cookies:
            cookie_value += f"{cookie['name']}={cookie['value']}; "

        zap = ZAPv2(apikey=apiKey, proxies={
            'http': f'http://{zap_address}:{zap_port}',
            'https': f'http://{zap_address}:{zap_port}'
        })

        # Add a custom cookies request header to every scanning request
        zap.replacer.add_rule(
            description="CookieHeader",
            enabled=True,
            matchtype="REQ_HEADER",
            matchregex=False,
            matchstring="Cookie",
            replacement=cookie_value
        )

        ''' ====================== SECTION 3: Classic Spider w/ Real-Time Tracking ====================== '''
        headers = {
            'Accept': 'application/json',
            "X-ZAP-API-Key": apiKey
        }

        print("--- Starting Classic Spider ---")
        # Request for scanning
        spider_params = {
            'url': scanning_url
            }
        spider_start_resp = requests.get(
            f"http://{proxy}/JSON/spider/action/scan/",
            params=spider_params,
            headers=headers
        )

        if spider_start_resp.status_code != 200:
            print(f"Error starting spider: {spider_start_resp.text}")
            return

        # Monitor progress & result
        spider_progress_url = f"http://{proxy}/JSON/spider/view/status/"
        spider_results_url  = f"http://{proxy}/JSON/spider/view/results/"

        tracked_urls = set()
        while True:
            time.sleep(5)
            progress_data = requests.get(spider_progress_url, headers=headers).json()
            pct = progress_data.get("status", "0")
            print(f"Spider Progress: {pct}%")

            # Fetch newly discovered URLs in real time
            results_json = requests.get(spider_results_url, headers=headers).json()
            discovered_list = results_json.get("results", [])
            new_urls = [u for u in discovered_list if u not in tracked_urls]

            for url in new_urls:
                print(f"  - Discovered: {url}")
            tracked_urls.update(new_urls)

            if pct == "100":
                # Spider done
                print("Classic Spider completed!")
                break

        # Combine spider-discovered URLs into global set
        all_urls.update(tracked_urls)
        print()

        ''' ====================== SECTION 4: AJAX Spider ====================== '''
        print("--- Starting AJAX Spider ---")
        # Let AJAX spider click known default elements
        requests.get(
            f"http://{proxy}/JSON/ajaxSpider/action/setOptionClickDefaultElems/",
            params={'Boolean': 'true'},
            headers=headers
        )

        # Request for scanning
        ajax_params = {
            'url': scanning_url
            }
        ajax_start_resp = requests.get(
            f"http://{proxy}/JSON/ajaxSpider/action/scan/",
            params=ajax_params,
            headers=headers
        )
        if ajax_start_resp.status_code != 200:
            print(f"Error starting AJAX spider: {ajax_start_resp.text}")
            return

        # Monitor progress & result
        ajax_status_url  = f"http://{proxy}/JSON/ajaxSpider/view/status/"
        ajax_results_url = f"http://{proxy}/JSON/ajaxSpider/view/fullResults/"

        while True:
            time.sleep(15)
            status_data = requests.get(ajax_status_url, headers=headers).json()
            stat = status_data.get("status", "unknown")
            print(f"AJAX Spider Status: {stat}")

            if stat == "stopped":
                # Once it's stopped, get the final results
                final_data = requests.get(ajax_results_url, headers=headers).json()
                # "fullResults" might be a string or a list
                results = final_data.get("fullResults", [])
                if isinstance(results, str):
                    print(f"WARNING: AJAX spider returned a string: {results}")
                    results_list = []
                else:
                    results_list = results

                print("\nAJAX Spider final results:")
                ajax_tracked_urls = set()
                for entry in results_list:
                    # Some entries might be strings, not dicts
                    if not isinstance(entry, dict):
                        print(f"WARNING: AJAX spider returned a non-dict item: {entry!r}")
                        continue

                    httpreq = entry.get("httprequest", {})
                    url = httpreq.get("url")
                    if url:
                        ajax_tracked_urls.add(url)
                        print(f"  - AJAX Discovered: {url}")

                all_urls.update(ajax_tracked_urls)
                print("AJAX Spider completed!")
                print("Note: InScope,OutOfScope,errors might be just the AJAX find no new links")
                break
            else:
                print("...AJAX spider still running, waiting...")

        print()

        ''' ====================== SECTION 5: Active Scan ====================== '''
        print("--- Starting Active Scan ---")
        # Request for scanning
        scan_data = {
            "url": scanning_url,
            "recurse": "true",
            "apikey": apiKey,
        }
        ascan_resp = requests.post(
            f"http://{proxy}/JSON/ascan/action/scan/",
            headers=headers,
            data=scan_data
        )
        ascan_json = ascan_resp.json()
        scan_id = ascan_json.get("scan")
        if not scan_id:
            print(f"Error starting active scan: {ascan_json}")
            return

        # Monitor progress & result
        while True:
            time.sleep(15)
            progress_data = requests.get(f"http://{proxy}/JSON/ascan/view/status/?scanId={scan_id}",
                                         headers=headers).json()
            pct = progress_data.get("status", "0")
            print(f"Scan Progress: {pct}%")

            if pct == "100":
                print("Active Scan completed!")
                break

        print()

        ''' ====================== SECTION 6: Generate JSON Report ====================== '''
        print("--- Generating JSON Report ---")
        report_params = {
            'sites': scanning_url,
            'reportFileName': "scan_report.json",
            'title': f"{scanning_url} scanning report",
            'template': "traditional-json"
        }
        json_report_resp = requests.get(
            f"http://{proxy}/JSON/reports/action/generate/",
            params=report_params,
            headers=headers
        )
        if json_report_resp.status_code == 200:
            print("JSON report generation requested successfully!")
        else:
            print(f"Error generating JSON report: {json_report_resp.text}")

    except Exception as e:
        print(f'An error occurred: {e}')

    finally:
        print("\nWriting discovered URLs to url.txt ...")
        with open("url.txt", "w", encoding="utf-8") as f:
            for url in sorted(all_urls):
                f.write(url + "\n")

        # Remove Cookie Header
        zap.replacer.remove_rule(description="CookieHeader")

        # Close Selenium Browser
        driver.quit()
        print("\n=== Script Complete ===")


if __name__ == "__main__":
    main()
