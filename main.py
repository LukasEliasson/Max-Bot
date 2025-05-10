import requests
from bs4 import BeautifulSoup

res = requests.get('https://web-images.futureordering.com/menus/maxburgers/se-sv-se-225-eatin.json.gz')
net = requests.get('https://www.max.se/maten/naringsvarden/', verify=False)

max_text: str = BeautifulSoup(net.text, 'html.parser').text

lines = max_text.splitlines()
filtered_lines = []
per_portion = {}
for line in lines:
    line = line.strip()
    filtered_lines.append(line)

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


under_75 = []

for id, product in max_menu['Refs'].items():
    if product['Price'] <= 75:
        under_75.append(product)


