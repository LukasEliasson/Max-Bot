import requests
from bs4 import BeautifulSoup
from stringmatch import Match

res = requests.get('https://web-images.futureordering.com/menus/maxburgers/se-sv-se-225-eatin.json.gz')
net = requests.get('https://www.max.se/maten/naringsvarden/', verify=False)

max_text: str = BeautifulSoup(net.text, 'html.parser').text

lines = max_text.splitlines()
filtered_lines = []
per_portion = {}
filtered_lines = [line.strip() for line in lines]

combination = []
for line in filtered_lines:
    if line == "":
        if len(combination) > 5:
            if combination[0] not in per_portion.keys():
                per_portion[combination[0]] = combination[1:]
        combination = []
    else:
        combination.append(line)

max_menu = res.json()
items = []

secret_menu_count = 1
secret_menu_ids = {}
print('Secret Menu:')
for id, product in max_menu['Refs'].items():
    name = product['Title']
    price = product['Price']
    
    if '15621' in product['Categories'].keys():
        print(f'{secret_menu_count}. {name} - {price} kr (ID: {product['Id']})')
        secret_menu_ids[secret_menu_count] = product['Id']
        secret_menu_count += 1
        continue

    if price < 9 or price > 75 or 'IsDefault' in product.keys():
        continue

    components = []

    if 'ord. pris' in name:
        replaced_name = name.replace('&', '+')
        components = replaced_name.split(' + ')
    else:
        components = [name]
    
    kcal = 0

    for component in components:

        # Find matching in per_portion
        match = Match()
        product_match = match.get_best_match(component, list(per_portion.keys()))

        if product_match:
            try:
                kcal += float(per_portion[product_match][2].replace(',', '.'))
            except Exception as e:
                raise Exception(e)
                
            items.append({
                'name': name,
                'price': price,
                'kcal': kcal
            })

def get_secret_menu_id(id):
    return secret_menu_ids[id]

best_combo = []
max_kcal = 0

def find_combinations(index, current_combo, total_price, total_kcal):
    global best_combo, max_kcal

    if total_price > 75:
        return
    if total_kcal > max_kcal:
        max_kcal = total_kcal
        best_combo = current_combo[:]

    for i in range(index, len(items)):
        item = items[i]

        find_combinations(
            i + 1,
            current_combo + [item],
            total_price + item['price'],
            total_kcal + item['kcal']
        )

find_combinations(0, [], 0, 0)

print('Bästa kombinationen:')
for item in best_combo:
    print(f'- {item['name']} ({item['price']} kr, {item['kcal']} kcal)')

print(f'Totalt: {sum(i['price'] for i in best_combo)} kr, {max_kcal:.0f} kcal')


