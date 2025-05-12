from selenium import webdriver
import requests

class Place_order():
    def __init__(self):
        payload = {
            "countryCode": "se",
            "cultureCode": "sv-se",
            "menuType": "eatin",
            "storeId": 225,
            "menuCultureCode": "sv-SE",
            "currencyIsoCode": "SEK",
            "salesChannel": {
                "type": "browser",
                "userAgentString": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
                "webClientVersion": "8.7.33"
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        self.id = requests.post("https://order.maxburgers.com/orders", json=payload, headers=headers)
        print(self.id.json())

        self.driver = webdriver.Chrome()

        self.driver.get("https://order.maxburgers.com/se/sv-se/categories?menuType=eatin&storeId=225")



order = Place_order()