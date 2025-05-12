import requests
from bs4 import BeautifulSoup
from stringmatch import Match
from itertools import combinations


class Combo:
    def __init__(self, products):
        self.products = products
        self.total_price = sum(p['price'] for p in products)
        self.total_kcal = sum(p['kcal'] for p in products)

    def __repr__(self):
        product_list = "\n".join(
            f"- {p['name']} ({p['price']} kr, {p['kcal']} kcal)" for p in self.products
        )
        return f"{product_list}\nTotalt: {self.total_price:.2f} kr, {self.total_kcal:.0f} kcal"


class Main:
    def __init__(self):
        self.per_portion = {}
        self.items = []
        self.top_combinations = []

    def fetch_data(self):
        print("Hämtar menyer och näringsvärden...")
        menu_res = requests.get('https://web-images.futureordering.com/menus/maxburgers/se-sv-se-225-eatin.json.gz')
        nutrition_res = requests.get('https://www.max.se/maten/naringsvarden/', verify=False)

        self.max_menu = menu_res.json()
        max_text = BeautifulSoup(nutrition_res.text, 'html.parser').text
        self.parse_nutrition_data(max_text)

    def parse_nutrition_data(self, text):
        lines = text.splitlines()
        filtered_lines = [line.strip() for line in lines]

        combination = []
        for line in filtered_lines:
            if line == "":
                if len(combination) > 5 and combination[0] not in self.per_portion:
                    self.per_portion[combination[0]] = combination[1:]
                combination = []
            else:
                combination.append(line)

    def build_items(self):
        print("Bygger produktlista...")
        for _, product in self.max_menu['Refs'].items():
            name = product['Title']
            price = product['Price']

            # Vi tar bort filtrering på kcal/kr och accepterar alla produkter mellan 9 och 75 kr
            if price < 9 or price > 75 or 'IsDefault' in product or '15621' in product.get('Categories', {}):
                continue

            components = [name.replace('&', '+')] if 'ord. pris' in name else [name]
            if '+' in components[0]:
                components = components[0].split(' + ')
                print(components, price)

            kcal = 0
            for component in components:
                match = Match()
                product_match = match.get_best_match(component, list(self.per_portion.keys()))
                print(f'Matched {component} to {product_match}')
                if product_match:
                    try:
                        kcal += float(self.per_portion[product_match][2].replace(',', '.'))
                    except Exception as e:
                        print(f"Fel vid kaloriparsning för {component}: {e}")

            # Lägg till produkten utan filtrering baserat på kcal/kr
            self.items.append({'name': name, 'price': price, 'kcal': kcal})

    def add_combination_if_top5(self, combo):
        if len(self.top_combinations) < 5:
            self.top_combinations.append(combo)
            self.top_combinations.sort(key=lambda c: c.total_kcal, reverse=True)
            print(f"Lade till ny kombination med {combo.total_kcal} kcal")
        else:
            if combo.total_kcal > self.top_combinations[-1].total_kcal:
                print(
                    f"Ersätter sämsta kombon ({self.top_combinations[-1].total_kcal} kcal) med ny ({combo.total_kcal} kcal)")
                self.top_combinations[-1] = combo
                self.top_combinations.sort(key=lambda c: c.total_kcal, reverse=True)

                                            #För att begränsa antal tittade kombinationer
    def generate_combinations(self, max_combinations=50000):
        print(f"Genererar upp till {max_combinations} kombinationer...")

        combo_count = 0  # Håller reda på antalet genererade kombinationer
        for r in range(1, len(self.items) + 1):
            for combo in combinations(self.items, r):
                if combo_count >= max_combinations:
                    return  # Stoppa när vi har genererat 100 kombinationer
                total_price = sum(item['price'] for item in combo)
                # Vi ser till att totalpriset inte överstiger 75 kr
                if total_price <= 75:
                    c = Combo(list(combo))
                    self.add_combination_if_top5(c)
                    combo_count += 1

    def run(self):
        self.fetch_data()
        self.build_items()
        self.generate_combinations()

        print("\nTopp 5 bästa kombinationer (mest kcal inom 75 kr):")
        for i, combo in enumerate(self.top_combinations, start=1):
            print(f"\n#{i}")
            print(combo)


if __name__ == "__main__":
    Main().run()

