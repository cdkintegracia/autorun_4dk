from fast_bitrix24 import Bitrix
import gspread
from authentication import authentication

"""
Bitrix
"""

# Считывание файла authentication.txt

webhook = authentication('Bitrix')
b = Bitrix(webhook)

companies = b.get_all('crm.company.list', {
    'select': [
        'UF_CRM_1660818061808',
        'TITLE'
    ]
}
                      )
contacts = b.get_all('crm.contact.list', {
    'select': [
        'ID',
        'NAME',
        'SECOND_NAME',
        'LAST_NAME',
        'UF_CRM_1660897963722',     # Вес сделок в связанных компаниях
    ]
}
                     )

field_names = {'UF_CRM_1660897963722': 'Вес сделок в связанных компаниях'}

# Формирование заголовков таблицы

contacts_title = []
for name_field in contacts[0]:
    if name_field in field_names:
        name_field = field_names[name_field]
    if name_field in ['LAST_NAME', 'SECOND_NAME']:
        continue
    contacts_title.append(name_field)

companies_title = []
for name_field in companies[0]:
    companies_title.append(name_field)


# Форматирование данных в списки для записи в таблицы

contacts_list = list(map(lambda x: [x['ID'], f"{x['NAME']} {x['SECOND_NAME']} {x['LAST_NAME']}",
                         x['UF_CRM_1660897963722']], contacts))
contacts_list.insert(0, contacts_title)

"""
Google sheets
"""

access = gspread.service_account(filename=authentication('Google Data Studio'))
spreadsheet = access.open('bitrix_data')
worksheet = spreadsheet.worksheet('contacts')
worksheet.clear()
worksheet.update('A1', contacts_list)
