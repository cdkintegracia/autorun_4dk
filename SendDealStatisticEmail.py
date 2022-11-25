from datetime import datetime, timedelta
import os.path

from fast_bitrix24 import Bitrix
import openpyxl


b = Bitrix('https://vc4dk.bitrix24.ru/rest/311/wkq0a0mvsvfmoseo/')

users_info = b.get_all('user.get', {'filter': {'ACTIVE': 'true'}})

def get_deals():
    current_day = datetime.now()
    filter_closedate_end = datetime.strftime(current_day + timedelta(days=31), '%Y-%m-%d')
    filter_closedate_start = datetime.strftime(current_day - timedelta(days=1), '%Y-%m-%d')
    b24_deals = b.get_all('crm.deal.list', {
        'select': [
            'ASSIGNED_BY_ID',
            'STAGE_ID',
            'UF_CRM_1657878818384'
        ],
        'filter': {
            '>CLOSEDATE': filter_closedate_start,
            '<CLOSEDATE': filter_closedate_end,
            'CATEGORY_ID': '1',
            'UF_CRM_1657878818384': [   # Группа
                '859',  # ИТС
                '905',  # Отчетность
            ]

        }})
    return b24_deals


def sort_users():
    global users_info
    departments = {
        'ГО4': [],
        'ГО3': [],
        'ОВ': [],
        'Прочие': [],
    }
    deal_stages = {

    }
    for user in users_info:
        if 29 in user['UF_DEPARTMENT']:
            departments['ГО4'].append(user['ID'])
        elif 27 in user['UF_DEPARTMENT']:
            departments['ГО3'].append(user['ID'])
        elif 225 in user['UF_DEPARTMENT']:
            departments['ОВ'].append(user['ID'])
        else:
            if user['ID'] == '109':     # Светлана Ридкобород
                continue
            departments['Прочие'].append(user['ID'])
    return departments


def sort_data_by_group(b24_deals, user_departments, stage_ids, group_name):
    global users_info
    group_id = {
        'ИТС': '859',
        'Отчетность': '905',
    }
    result = [
        ['Состояние сделок, заканчивающихся в течение след. 30 дней'],
        ['', '', 'Услуга активна', 'Счет сформирован', 'Счет отправлен', 'Нет оплаты', 'Ждем решения клиента' 'Услуга завершена', 'Отказ от сопровождения']
    ]
    for department in user_departments:
        department_row = [department, '', ]
        for stage in stage_ids:
            filtered_deals_count = len(
                list(
                    filter(
                        lambda x: x['STAGE_ID'] == stage
                                  and x['ASSIGNED_BY_ID'] in user_departments[department]
                                  and x['UF_CRM_1657878818384'] == group_id[group_name],
                        b24_deals
                    )))
            department_row.append(filtered_deals_count)
        result.append(department_row)

        for user_id in user_departments[department]:
            user_info = list(filter(lambda x: x['ID'] == user_id, users_info))[0]
            user_name = f"{user_info['LAST_NAME']} {user_info['NAME']}"
            print(user_name, user_id)
            user_row = ['', user_name]
            for stage in stage_ids:
                filtered_deals_count = len(
                    list(
                        filter(
                            lambda x: x['STAGE_ID'] == stage
                            and x['ASSIGNED_BY_ID'] == user_id
                            and x['UF_CRM_1657878818384'] == group_id[group_name],
                            b24_deals
                        )))
                user_row.append(filtered_deals_count)
            result.append(user_row)
    return result


def write_data_to_xlsx(data, report_name):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'ИТС'
    if os.path.exists(report_name):
        workbook = openpyxl.load_workbook(report_name)
        worksheet = workbook.create_sheet('Отчетность')

    for row in data:
        worksheet.append(row)
    workbook.save(report_name)




def send_deal_statistic_email():
    stage_ids = [
        'C1:NEW',           # Услуга активна
        'C1:UC_0KJKTY',     # Счет сформирован
        'C1:UC_3J0IH6',     # Счет отправлен клиенту
        'C1:UC_KZSOR2',     # Нет оплаты
        'C1:UC_VQ5HJD',     # Ждём решения клиента
        'C1:WON',           # Услуга завершена
        'C1:LOSE',          # Отказ от сопровождения
    ]
    group_names = ['ИТС', 'Отчетность']
    b24_deals = get_deals()
    user_departments = sort_users()
    for group in group_names:
        data_to_write = sort_data_by_group(b24_deals, user_departments, stage_ids, group)
        write_data_to_xlsx(data_to_write, 'text.xlsx')








send_deal_statistic_email()


