from seleniumwire import webdriver
import requests
import time
import gzip
from io import BytesIO
import json

class Place_order():
    def __init__(self,ids):

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
                        found = True
                        break

        self.order_items(ids)

    def order_items(self,ids):
        url = f"https://order.maxburgers.com/orders/{self.order_id}/products"
        payload = {
    "products": [ {"Id": id} for id in ids]
        }
        order = requests.post(url, json=payload)
        print(order)



order = Place_order([])