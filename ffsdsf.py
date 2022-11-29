from fast_bitrix24 import Bitrix

from ElementCallStatistic import create_element

b = Bitrix('https://vc4dk.bitrix24.ru/rest/311/wkq0a0mvsvfmoseo/')

month_codes = {
    'Январь': '2215',
    'Февраль': '2217',
    'Март': '2219',
    'Апрель': '2221',
    'Май': '2223',
    'Июнь': '2225',
    'Июль': '2227',
    'Август': '2229',
    'Сентябрь': '2231',
    'Октябрь': '2233',
    'Ноябрь': '2235',
    'Декабрь': '2237'
}
year_codes = {
    '2022': '2239',
    '2023': '2241'
}

companies = b.get_all('crm.company.list')
elements = b.get_all('lists.element.get', {'IBLOCK_TYPE_ID': 'lists', 'IBLOCK_ID': '175', 'filter': {'NAME': f"Декабрь 2022"}})
elements = list(filter(lambda x: 'PROPERTY_1299' in x, elements))
elements = list(map(lambda x: list(x['PROPERTY_1299'].values())[0], elements))
companies = list(filter(lambda x: x['ID'] not in elements, companies))
count = 0
for company in companies:
    create_element(company['ID'])
    count += 1
    print(f'{count} | {len(companies)}')


