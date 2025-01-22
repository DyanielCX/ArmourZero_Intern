import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


''' Website Information '''
# Target URLs (Change to your own information)
scanning_url = 'https://webapp3.wimify.xyz/profile'
login_url = 'https://webapp3.wimify.xyz/#/login'
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
    time.sleep(2)  # Wait for the page to load
    
    # Automate login
    driver.find_element(By.NAME, usrnm_varNAME).send_keys(username)
    driver.find_element(By.NAME, passw_varNAME).send_keys(password)
    driver.find_element(By.NAME, passw_varNAME).send_keys(Keys.RETURN)
    time.sleep(5)

    # Retrieve and format the authentication session
    cookies = driver.get_cookies()
    zap_cookies = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
    print(zap_cookies)
    time.sleep(10)

    print('\nLogin completed!')

except Exception as e:
    print(f'An error occurred: {e}')

finally:
    # Close the Selenium WebDriver
    driver.quit()