import csv
from datetime import datetime
import os
import time

from fast_bitrix24 import Bitrix
import yadisk

from authentication import authentication
import field_values


b = Bitrix(authentication('Bitrix'))
y = yadisk.YaDisk(token=authentication('Yandex'))


def main(filename, entity, companies, entity_id, folder_path, category_id):

    if entity == 'deal':
        data = b.get_all('crm.deal.list', {
            'select': ['*', 'UF_*'],
            'filter': {
                'CATEGORY_ID': category_id
            }
        })
    elif entity == 'item':
        data = b.get_all('crm.item.list', {
            'entityTypeId': entity_id,
            'select': ['*', 'UF_*']
        })

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
    '''
    filename = f'{filename}_{datetime.now().strftime("%d_%m_%Y")}.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(titles)
        for row in data:
            writer.writerow(list(row.values()))

    with open(filename, 'rb') as file:
        y.upload(file, f'{folder_path}/{filename}')
    os.remove(filename)
    '''
    filename = f'{filename}_{datetime.now().strftime("%d_%m_%Y")}.csv'
    # записываем локально
    with open(filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(titles)
        for row in data:
            writer.writerow(list(row.values()))

    # загружаем на Яндекс.Диск с перезаписью
    upload_path = f'{folder_path}/{filename}'
    with open(filename, 'rb') as file:
        try:
            # если поддерживается overwrite:
            y.upload(file, upload_path, overwrite=True, timeout=(10,300))
        except TypeError:
            # fallback для старых версий yadisk
            try:
                y.upload(file, upload_path)
            except PathExistsError:
                y.remove(upload_path)
                file.seek(0)
                y.upload(file, upload_path)

    os.remove(filename)

def create_backup_files():
    data_types = [
        {'filename': 'Сопровождение', 'entity': 'deal', 'entity_id': None, 'category_id': '1'},
        {'filename': 'Продажи', 'entity': 'deal', 'entity_id': None, 'category_id': '9'},
        {'filename': 'Адаптация', 'entity': 'deal', 'entity_id': None, 'category_id': '19'},
        {'filename': 'Источники_продаж', 'entity': 'item', 'entity_id': '133', 'category_id': None},
        {'filename': 'Досье_клиента', 'entity': 'item', 'entity_id': '186', 'category_id': None},
        {'filename': 'Проработка_по_сервисам', 'entity': 'item', 'entity_id': '150', 'category_id': None},
        {'filename': 'Доступы_и_файлы', 'entity': 'item', 'entity_id': '165', 'category_id': None},
        {'filename': 'Инфо', 'entity': 'item', 'entity_id': '141', 'category_id': None},
        {'filename': 'Лиды Фреш 1С', 'entity': 'deal', 'entity_id': None, 'category_id': '25'}
    ]
    companies = b.get_all('crm.company.list', {
        'select': ['*']
    })

    folder_path = f"/Бэкапы ЧДК/{datetime.now().strftime('%d.%m.%Y')}"
    y.mkdir(folder_path)
    for data_type in data_types:
        main(data_type['filename'], data_type['entity'], companies, data_type['entity_id'], folder_path, category_id=data_type['category_id'])
        time.sleep (15)
    b.call('im.notify.system.add', {
        'USER_ID': 1,
        'MESSAGE': f'Копии созданы'})

if __name__ == '__main__':
    create_backup_files()
