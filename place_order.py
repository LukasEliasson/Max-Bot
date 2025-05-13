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

class Place_orders():
    def __init__(self,ids):
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

        with open("cookies.json", "r") as f:
            cookies = json.load(f)

        for cookie in cookies:
            # Remove "sameSite" if not accepted by Selenium
            cookie.pop('sameSite', None)
            self.driver.add_cookie(cookie)

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
        self.buy_order(1,2,3)

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


    def buy_order(self,card,date,pin):
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


        input("Press Enter to continue...")
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



order = Place_orders([18265])