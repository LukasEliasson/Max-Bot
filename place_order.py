from seleniumwire import webdriver
import requests
import time
import gzip
from io import BytesIO
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from fake_headers import Headers
from main import get_secret_menu_id

try:
    with open('cookies.json', 'x') as f:
        json.dump({}, f)
except FileExistsError:
    pass

product_ids = []

class Place_orders():
    def __init__(self,ids):

        name = input('\nName >>> ')

        print('\nSelect items to order (type "exit" when done):')
        selecting = True
        while selecting:
            selection = input('\nChoose number (1-35) >>> ')

            if selection.lower() == 'exit':
                selecting = False
                continue

            try:
                product_ids.append(get_secret_menu_id(int(selection)))
            except:
                print('\nNot a valid number.')
            finally:
                print(f'\nProducts in cart: {product_ids}')

        self.headers = Headers(browser="chrome", os="win", headers=False).generate()

        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """
        })
        self.driver.get(f"https://order.maxburgers.com/se/sv-se/categories?menuType=eatin&storeId=225")  # Load domain first!

        try:
            self.add_cookie(name)
        except KeyError:
            self.create_cookie(name)

        self.driver.refresh()
        time.sleep(5)

        found = False
        while not found:
            for request in self.driver.requests:
                if request.method == 'POST' and "https://order.maxburgers.com/orders" in request.url:
                    if request.response:
                        print("Status:", request.response.status_code)

                        compressed = request.response.body
                        decompressed = gzip.decompress(compressed).decode('utf-8')
                        self.data = json.loads(decompressed)
                        self.order_id = self.data["orderId"]
                        print("Order ID:", self.order_id)
                        found = True
                        break
        time.sleep(2)
        self.order_items(ids)
        time.sleep(1)
        self.buy_order(False)

        input("Press Enter to continue...")

    def order_items(self,ids):
        session = requests.Session()

        for cookie in self.driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        url = f"https://order.maxburgers.com/orders/{self.order_id}/products"

        payload = {
    "products": [ {"Id": id} for id in ids]
        }
        order = session.post(url, json=payload, headers=self.headers)
        print(order)


    def buy_order(self,buy,card = None,date = None,pin = None):
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "cookie")))
            button.click()
        except:
            print("no popup")
        # menu
        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "nav")))
        button.click()

        # time selector
        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "li.pure-u-1.taptic")))
        button.click()

        # confirm time
        
        button = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "next")))
        button.click()


        if buy:
            try:
                # bascket
                button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "button-basket")))
                button.click()
            except:
                print("no basket button")

            button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "button-checkout")))
            button.click()

            # go to checkout
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "next")))
            button.click()



            # select card
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,"//li[contains(@ng-click, 'select(paymentOpt)') and contains(., 'Nytt kredit- / betalkort')]")))
            button.click()


            #contine
            try:
                button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "button-pay")))
                button.click()
            except:
                button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "button-checkout")))
                button.click()


            time.sleep(15)

            #card, date, pin

            inputs = self.driver.find_elements(By.CLASS_NAME, "js-iframe-input input-field")

            for input_field in inputs:
                if "1234 5678 9012 3456" in input_field.get_attribute("placeholder").lower():
                    input_field.send_keys("4111 1111 1111 1111")
                elif "mm/åå" in input_field.get_attribute("placeholder").lower():
                    input_field.send_keys("0226")
                elif "siffror" in input_field.get_attribute("placeholder").lower():
                    input_field.send_keys("256")

    def load_cookies(self):
        with open("cookies.json", "r") as f:
            cookies = json.load(f)
            return cookies

    def add_cookie(self, name):
        cookies = self.load_cookies()

        if name not in cookies.keys():
            raise KeyError('Name not found in cookies file. Please create a cookie')

        for cookie in cookies[name]:
            # Remove "sameSite" if not accepted by Selenium
            cookie.pop('sameSite', None)
            self.driver.add_cookie(cookie)

    def create_cookie(self, name):
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "cookie")))
            button.click()
        except:
            print("no popup")
        
        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "nav")))
        button.click()
        
        time.sleep(1)

        login_link = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Logga in / registrera")))
        login_link.click()

        try:
            WebDriverWait(self.driver, 300).until(
                EC.url_to_be('https://order.maxburgers.com/se/sv-se/categories?menuType=eatin&storeId=225')
            )

            driver_cookies = self.driver.get_cookies()
            cookies_data = self.load_cookies()
            cookies_data[name] = driver_cookies
            with open('cookies.json', 'w', encoding='utf-8') as f:
                try:
                    json.dump(cookies_data, f)
                except Exception as e:
                    print(f'Error vid sparning av cookie: {e}')
                    
        except Exception as e:
            print(f'Error vid vänta på inloggning: {e}')

order = Place_orders(product_ids)