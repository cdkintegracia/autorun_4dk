import csv
from datetime import datetime

from fast_bitrix24 import Bitrix

from authentication import authentication
import field_values


b = Bitrix(authentication('Bitrix'))


def main(filename, entity, companies, entity_id):

    if entity == 'deal':
        data = b.get_all('crm.deal.list', {
            'select': ['*', 'UF_*'],
            'filter': {
                'CATEGORY_ID': '1' if filename == 'Сопровождение' else '9'
            }
        })
    elif entity == 'item':
        data = b.get_all('crm.item.list', {
            'entityTypeId': entity_id,
            'select': ['*', 'UF_*']
        })
    elif entity == 'company':
        data = companies
    else:
        data = b.get_all(f'crm.{entity}.list', {
            'select': ['*', 'UF_*'],
        })

    if entity == 'item':
        fields = b.get_all(f'crm.{entity}.fields', {
            'entityTypeId': entity_id
        })['fields']
    else:
        fields = b.get_all(f'crm.{entity}.fields')
        fields_values = b.get_all(f'crm.{entity}.userfield.list')

    # Создание заголовков
    titles = []
    for title_code in data[0]:
        if 'UF' in title_code:
            titles.append(fields[title_code]['listLabel'])
        else:
            if entity == 'item':
                if title_code in fields:
                    titles.append(fields[title_code]['title'])
                else:
                    titles.append(title_code)
            else:
                titles.append(fields[title_code]['title'])

    # Преобразование значений
    for row_number in range(len(data)):
        for key in data[row_number]:
            if not data[row_number][key]:
                continue
            if key in ['TYPE_ID', 'COMPANY_TYPE', 'INDUSTRY', 'EMPLOYEES']:
                try:
                    data[row_number][key] = field_values.category_types[data[row_number][key]]
                except:
                    pass
            elif key in ['STAGE_ID', 'stageId']:
                data[row_number][key] = field_values.stage_ids[data[row_number][key]]
            elif key in ['COMPANY_ID', 'companyId']:
                company_info = list(filter(lambda x: x['ID'] == str(data[row_number][key]), companies))
                if company_info:
                    data[row_number][key] = f"{data[row_number][key]} {company_info[0]['TITLE']}"
            else:
                # Значение в дату
                try:
                    d = datetime.fromisoformat(data[row_number][key])
                    data[row_number][key] = d.strftime('%d.%m.%Y %H:%M:%S')
                except:
                    # Преобразование списочного значения
                    if entity != 'item':
                        is_field_enumeration = list(filter(lambda x: x['FIELD_NAME'] == key and x['USER_TYPE_ID'] == 'enumeration', fields_values))
                        if is_field_enumeration:
                            value = list(filter(lambda x: x['ID'] == data[row_number][key], is_field_enumeration[0]['LIST']))
                            if value:
                                data[row_number][key] = value[0]['VALUE']
                    else:
                        if key in fields and fields[key]['type'] == 'enumeration':
                            data[row_number][key] = list(filter(lambda x: x['ID'] == str(data[row_number][key]), fields[key]['items']))[0]['VALUE']


    with open(f'{filename}_{datetime.now().strftime("%d_%m_%Y")}.csv', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(titles)
        for row in data:
            writer.writerow(list(row.values()))


def create_backup_files():
    data_types = [
        {'filename': 'Сопровождение', 'entity': 'deal', 'entity_id': None},
        {'filename': 'Продажи', 'entity': 'deal', 'entity_id': None},
        {'filename': 'Контакты', 'entity': 'contact', 'entity_id': None},
        {'filename': 'Компании', 'entity': 'company', 'entity_id': None},
        {'filename': 'Источники_продаж', 'entity': 'item', 'entity_id': '133'},
        {'filename': 'Досье_клиента', 'entity': 'item', 'entity_id': '186'}
    ]
    companies = b.get_all('crm.company.list', {
        'select': ['*', 'UF_*']
    })
    for data_type in data_types:
        main(data_type['filename'], data_type['entity'], companies, data_type['entity_id'])


create_backup_files()
