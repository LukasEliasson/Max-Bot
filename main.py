import requests
from bs4 import BeautifulSoup

res = requests.get('https://web-images.futureordering.com/menus/maxburgers/se-sv-se-225-eatin.json.gz')
net = requests.get('https://www.max.se/maten/naringsvarden/', verify=False)

max_text: str = BeautifulSoup(net.text, 'html.parser').text

lines = max_text.splitlines()
filtered_lines = []
per_portion = {}
banned_words = ["Integritetsmeddelande",]
for line in lines:
    line = line.strip()
    if line != '':
        filtered_lines.append(line)

filtered_lines = filtered_lines[73:]

value_counter = 0
latest_key = ""
table_headers = [
    'Supreme Green',
    'Burgare',
    'Kyckling, fisk & sallad',
    'Tillbehör & Dip',
    'Desserter & Lyxshake',
    'Dryck & Kaffe',
]
between_tables = False
total_count = 0
for line in filtered_lines:
    if total_count >= 500:
        break

    if not line in per_portion.keys():
        if line in table_headers:
            between_tables = True
            value_counter = 0
            print(f'{line}: Set between tables to True')
        elif between_tables:
            if line == '(i kg)':
                between_tables = False
                print(f'{line}: Set between tables to False')
            else:
                print(f'{line}: Skipped')
        elif value_counter == 0:
            per_portion[line] = []
            latest_key = line
            value_counter += 1
            print(f'{line}: New key')
        elif len(line) > 13:
            value_counter = 0
            print(f'{line}: Set value counter to 0 due to long line.')
        elif value_counter < 10:
            per_portion[latest_key].append(line)
            value_counter += 1
            print(f'{line}: Set value ({value_counter})')
        else:
            value_counter = 0
            print(f'{line}: Set value counter to 0.')

        total_count += 1

max_menu = res.json()


under_75 = []

for id, product in max_menu['Refs'].items():
    if product['Price'] <= 75:
        under_75.append(product)


