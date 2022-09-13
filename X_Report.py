from time import strftime

from fast_bitrix24 import Bitrix
import gspread

from authentication import authentication

b = Bitrix(authentication('Bitrix'))

def main():

    group_string = {
        '859': 'ИТС',
        '905': 'Отчетность',
        '907': 'Сервисы ИТС',
        '903': 'Товар',
    }

    department_string = {
        '1': '4DK',
        '5': 'ЦС',
        '27': 'ГО3',
        '29': 'ГО4',
        '225': 'ОВ',
        '231': 'ЛК',
        '235': 'Битрикс',
        '233': 'Служебные',
    }

    month_string = {
            '01': 'Январь',
            '02': 'Февраль',
            '03': 'Март',
            '04': 'Апрель',
            '05': 'Май',
            '06': 'Июнь',
            '07': 'Июль',
            '08': 'Август',
            '09': 'Сентябрь',
            '10': 'Октябрь',
            '11': 'Ноябрь',
            '12': 'Декабрь'
        }


    deals = b.get_all('crm.deal.list', {

        'select': [
            'TITLE',    # Название
            'TYPE_ID',  # Тип
            'STAGE_ID',  # Стадия
            'UF_CRM_1657878818384',     # Группа
            'ASSIGNED_BY_ID',       # Ответственный
            'COMPANY_ID',       # Компания
            'UF_CRM_1657533812',    # Продавец
            'UF_CRM_1657549699',    # Дата перехода в отвал
            'UF_CRM_1662714299',    # СсылкаНаИсточникПродажи
            'OPPORTUNITY',
        ],

        'filter': {
            'CATEGORY_ID': '1'
        }
    }
                      )

    count = 0
    user_names = {}
    for deal in deals:

        # Дата продажи
        if deal['UF_CRM_1662714299']:
                print(deal['ID'])
                smart = b.get_all('crm.item.list', {'entityTypeId': '133', 'filter': {'ID': deal['UF_CRM_1662714299']}})[0]
                deal['UF_CRM_1662714299'] = f"{smart['createdTime'][8:10]}.{smart['createdTime'][5:7]}.{smart['createdTime'][:4]}"

        # Дата отвала
        if deal['UF_CRM_1657549699']:
            deal['UF_CRM_1657549699'] = f"{deal['UF_CRM_1657549699'][8:10]}.{deal['UF_CRM_1657549699'][5:7]}.{deal['UF_CRM_1657549699'][:4]}"

        # Название компании
        try:
            company_name = b.get_all('crm.company.list', {'select': ['TITLE'], 'filter': {'ID': deal['COMPANY_ID']}})[0]['TITLE']
            deal['COMPANY_ID'] = company_name
        except:
            pass

        # Ответственный
        if deal['ASSIGNED_BY_ID'] not in user_names:
            user_data = b.get_all('user.get', {'select': ['UF_DEPARTMENT', 'NAME', 'LAST_NAME'], 'ID': deal['ASSIGNED_BY_ID']})[0]
            user_name = f"{user_data['NAME']} {user_data['LAST_NAME']}"
            try:
                user_department = department_string[str(user_data['UF_DEPARTMENT'][0])]
            except:
                user_department = user_data['UF_DEPARTMENT'][0]
            user_names.setdefault(deal['ASSIGNED_BY_ID'], [user_name, user_department])
        deal.setdefault('Подразделение', user_names[deal['ASSIGNED_BY_ID']][1])
        deal['ASSIGNED_BY_ID'] = user_names[deal['ASSIGNED_BY_ID']][0]

        # Продавец
        try:
            if deal['UF_CRM_1657533812'] not in user_names:
                user_data = b.get_all('user.get', {'ID': deal['UF_CRM_1657533812']})[0]
                user_name = f"{user_data['NAME']} {user_data['LAST_NAME']}"
                try:
                    user_department = department_string[user_data['UF_DEPARTMENT'][0]]
                except:
                    user_department = user_data['UF_DEPARTMENT'][0]
                user_names.setdefault(deal['UF_CRM_1657533812'], [user_name, user_department])
            deal['UF_CRM_1657533812'] = user_names[deal['UF_CRM_1657533812']][0]
        except:
            pass

        # Группа
        try:
            deal['UF_CRM_1657878818384'] = group_string[deal['UF_CRM_1657878818384']]
        except:
            pass

        count += 1
        print(f"{count} | {len(deals)}")

    titles = list(deals[0].keys())
    data_list = [titles]
    deal_values = list(map(lambda x: x.values(), deals))

    for values in deal_values:
        data_list.append(list(values))

    access = gspread.service_account(f"/root/credentials/bitrix24-data-studio-2278c7bfb1a7.json")
    worksheet_date = month_string[strftime('%m')]
    with open('/root/autorun_4dk/X_Report config.txt', 'r') as file:
        file_name = file.read()
    spreadsheet = access.open(file_name)
    try:
        worksheet = spreadsheet.add_worksheet(title=worksheet_date, rows=1, cols=1)
    except gspread.exceptions.APIError:
        worksheet = spreadsheet.worksheet(worksheet_date)
    worksheet.clear()
    worksheet.update('A1', data_list)

if __name__ == '__main__':
    main()