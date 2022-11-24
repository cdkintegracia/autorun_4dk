from datetime import datetime, timedelta

from fast_bitrix24 import Bitrix


b = Bitrix('https://vc4dk.bitrix24.ru/rest/311/wkq0a0mvsvfmoseo/')

users_info = b.get_all('user.get')

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


def write_data_to_xlsx(sheet_name):

    pass


def sort_users():
    global users_info
    departments = {
        'ГО4': {},
        'ГО3': {},
        'ОВ': {},
        'Прочие': {},
    }
    deal_stages = {

    }
    for user in users_info:
        if 29 in user['UF_DEPARTMENT']:
            departments['ГО4'].setdefault(user['ID'], {})
        elif 27 in user['UF_DEPARTMENT']:
            departments['ГО3'].setdefault(user['ID'], {})
        elif 225 in user['UF_DEPARTMENT']:
            departments['ОВ'].setdefault(user['ID'], {})
        else:
            if user['ID'] == '109':     # Светлана Ридкобород
                continue
            departments['Прочие'].setdefault(user['ID'], {})
    return departments


def sort_deals():
    b24_deals = get_deals()
    user_departments = sort_users()
    for deal in b24_deals:
        for department_key in user_departments:
            if deal['ASSIGNED_BY_ID'] in



sort_deals()
print(sort_users())


