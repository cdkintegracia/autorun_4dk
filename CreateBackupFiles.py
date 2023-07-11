import csv
from datetime import datetime

from fast_bitrix24 import Bitrix

from authentication import authentication


b = Bitrix(authentication('Bitrix'))


fields = b.get_all('crm.deal.fields')
fields = b.get_all('crm.deal.userfield.list')
for i in fields:
    print(i)
exit()
data = b.get_all('crm.deal.list', {
    'select': ['*', 'UF_*'],
    'filter': {
        'CATEGORY_ID': '1'
    }
})
titles = []
for title_code in data[0]:
    if 'UF' in title_code:
        titles.append(fields[title_code]['listLabel'])
    else:
        titles.append(fields[title_code]['title'])

with open(f'Сопровождение_{datetime.now().strftime("%d_%m_%Y")}.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(titles)
    for row in data:
        writer.writerow(list(row.values()))

