from datetime import datetime
from datetime import timedelta
from time import time

from fast_bitrix24 import Bitrix

from authentication import authentication

b = Bitrix(authentication('Bitrix'))

def main():
    crm_dct = {
        '1': ['Лид:', 'lead', 'L'],
        '2': ['Сделка:', 'deal', 'D'],
        '3': ['Контакт:', 'contact', 'C'],
        '4': ['Компания', 'company', 'CO'],
        '31': ['Счет', 'smart_invoice', 'SI'],
    }
    current_date = datetime.utcnow().strftime('%Y %m %d')
    current_date = datetime.strptime(current_date, '%Y %m %d')
    date_filter = current_date - timedelta(days=3)
    date_filter = date_filter.strftime('%Y-%m-%d')
    read_check_date = current_date.strftime('%Y-%m-%d')


    not_filtred_mails = b.get_all('crm.activity.list', {'filter': {'PROVIDER_TYPE_ID': 'EMAIL', '>=CREATED': date_filter, 'DIRECTION': '2'}})
    mails = []
    for mail in not_filtred_mails:
        if date_filter in mail['CREATED']:
            mails.append(mail)

    current_date = datetime.utcnow().strftime('%Y %m %d')
    current_date = datetime.strptime(current_date, '%Y %m %d')

    for mail in mails:
        created = mail['CREATED'].split('-')
        created[2] = created[2][:2]
        date_created = datetime.strptime('-'.join(created), '%Y-%m-%d')
        different = current_date - date_created
        if different.days > 0:
            if 'READ_CONFIRMED' not in mail['SETTINGS']:
                b.call('im.notify.system.add',
                       {'USER_ID': mail['AUTHOR_ID'],
                        'MESSAGE': f'Письмо не было прочитано или доставлено в срок.\n'
                        f'{crm_dct[mail["OWNER_TYPE_ID"]][0]} https://vc4dk.bitrix24.ru/crm/{crm_dct[mail["OWNER_TYPE_ID"]][1]}/details/{mail["OWNER_ID"]}/'})

                # Создание элемента
                assigned = b.get_all(f'crm.{crm_dct[mail["OWNER_TYPE_ID"]][1]}.list', {'filter': {'ID': mail['OWNER_ID']}})[0][
                    'ASSIGNED_BY_ID']
                check = b.get_all('lists.element.get', {'IBLOCK_TYPE_ID': 'lists', 'IBLOCK_ID': '185', 'filter': {'NAME': mail['ID']}})
                if not check:
                    b.call('lists.element.add', {
                        'IBLOCK_TYPE_ID': 'lists',
                        'IBLOCK_ID': '185',
                        'ELEMENT_CODE': time(),
                        'fields': {
                            'NAME': mail['ID'],
                            'PROPERTY_1319': f"{crm_dct[mail['OWNER_TYPE_ID']][2]}_{mail['OWNER_ID']}",
                            'PROPERTY_1321': date_created,
                            'PROPERTY_1327': mail['SETTINGS']['EMAIL_META']['to'],
                            'PROPERTY_1329': assigned,
                        }})

    # Прочтение письма
    elements = b.get_all('lists.element.get', {
        'IBLOCK_TYPE_ID': 'lists',
        'IBLOCK_ID': '185',
        'filter': {'PROPERTY_1343': 'None'}})
    for element in elements:
        mail = b.get_all('crm.activity.list', {
            'filter': {'PROVIDER_TYPE_ID': 'EMAIL', 'ID': element['NAME']}})

        if 'READ_CONFIRMED' in mail:
            b.call('lists.element.update', {
                'IBLOCK_TYPE_ID': 'lists',
                'IBLOCK_ID': '185',
                'ELEMENT_ID': element['ID'],
                'fields': {
                    'NAME': element['NAME'],
                    'PROPERTY_1319': element['PROPERTY_1319'],
                    'PROPERTY_1321': element['PROPERTY_1321'],
                    'PROPERTY_1325': element['PROPERTY_1325'],
                    'PROPERTY_1327': element['PROPERTY_1327'],
                    'PROPERTY_1329': element['PROPERTY_1329'],
                    'PROPERTY_1343': read_check_date,
                }
            }
                   )

if __name__ == '__main__':
    main()