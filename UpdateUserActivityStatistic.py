from datetime import datetime, timedelta

from fast_bitrix24 import Bitrix
import gspread

from authentication import authentication


b = Bitrix(authentication('Bitrix'))
month_int_names = {
        1: 'Январь',
        2: 'Февраль',
        3: 'Март',
        4: 'Апрель',
        5: 'Май',
        6: 'Июнь',
        7: 'Июль',
        8: 'Август',
        9: 'Сентябрь',
        10: 'Октябрь',
        11: 'Ноябрь',
        12: 'Декабрь',
    }


def update_user_activity_statistic():
    week_day = datetime.today().isoweekday()
    if week_day in [6, 7]:  # Выходные
        return

    users_info = b.get_all('user.get', {
        'filter': {
            '!ID': [
                '209',  # Администратор ТЛП
                '213',  # Администратор
                '91',  # Дежурный администратор
                '235',  # Тестовый аккаунт
                '201',  # Отдел внедрения
                '173',  # Робот Задач
                '17',  # Специалист ЛК
                '113',  # Диспетчер ЛК
                '333',  # Отчет Сервисный выезд
                '59',  # Иван Иванов
                '205',  # b24_asterisk
                '139',  # Антон Степанов
            ],
            'ACTIVE': 'true'
        }})
    departments = b.get_all('department.get')
    file_name = f'Активность пользователей {datetime.now().year}'
    sheet_name = month_int_names[datetime.now().month]
    try:
        google_access = gspread.service_account(f"/root/credentials/{authentication('Google')}")
    except FileNotFoundError:
        google_access = gspread.service_account(f"C:\\Users\\mok\\Documents\\GitHub\\{authentication('Google')}")
    spreadsheet = google_access.open(file_name)

    try:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=36)
        titles = [
            ['Пользователь', 'Отдел', 'Активность', 'Всего']
        ]
        users = list(map(lambda x: [f"{x['NAME']} {x['LAST_NAME']}"], users_info))
        users = list(sorted(users, key=lambda x: x[0].split()[1]))
        for user in users:
            department_name = ''
            user_info = list(filter(lambda x: x['NAME'] == user[0].split()[0] and x['LAST_NAME'] == user[0].split()[1], users_info))[0]
            if user_info['UF_DEPARTMENT']:
                user_department = list(filter(lambda x: str(user_info['UF_DEPARTMENT'][0]) == str(x['ID']), departments))[0]
                department_name = user_department['NAME']
            titles.append([' '.join(user), department_name])
            titles.append([' '.join(user), department_name,  'Завершенные задачи'])
            titles.append([' '.join(user), department_name, 'Исходящие звонки'])
            titles.append([' '.join(user), department_name, 'Входящие звонки'])
            titles.append([' '.join(user), department_name, 'Отправленные письма'])
            titles.append([' '.join(user), department_name, 'Обращений в 1С:Коннект'])
        worksheet.update('A1', titles)

    except gspread.exceptions.APIError:
        worksheet = spreadsheet.worksheet(sheet_name)

    worksheet_values = worksheet.get_all_values()
    new_worksheet_data = []

    date_filter = datetime.strftime(datetime.now(), '%Y-%m-%d')
    date_filter = '2023-03-15'
    end_date_filter = datetime.strftime(datetime.now() + timedelta(days=1), '%Y-%m-%d')
    end_date_filter = '2023-03-16'
    calls = b.get_all('voximplant.statistic.get', {'filter': {'>=CALL_START_DATE': date_filter, 'CALL_FAILED_CODE': '200', '<CALL_START_DATE': end_date_filter}})
    sent_email = b.get_all('crm.activity.list', {'filter': {'PROVIDER_TYPE_ID': 'EMAIL', '>=CREATED': date_filter, 'DIRECTION': '2', '<CREATED': end_date_filter}})
    tasks = b.get_all('tasks.task.list', {'filter': {'>=CLOSED_DATE': date_filter, '<CLOSED_DATE': end_date_filter}})
    user_name = ''
    user_id = ''
    for row in worksheet_values:
        activities_sum = ''
        if 'Пользователь' in row:
            row.insert(-1, datetime.strftime(datetime.now() - timedelta(days=1), '%d.%m.%Y'))
        elif row[2] == '':
            user_name = row[0]
            user_id = list(filter(lambda x: x['NAME'] == user_name.split()[0] and x['LAST_NAME'] == user_name.split()[1], users_info))
            if user_id:
                user_id = user_id[0]['ID']
            else:
                new_worksheet_data.append(row)
        elif 'Завершенные задачи' in row:
            user_closed_tasks = list(filter(lambda x: x['responsibleId'] == user_id and '1С:Коннект' not in x['title'], tasks))
            row[-1] = (len(user_closed_tasks))
            activities_sum = sum(list(map(lambda x: int(x), row[3:])))
        elif 'Исходящие звонки' in row:
            user_outgoing_calls = list(filter(lambda x: x['PORTAL_USER_ID'] == user_id and int(x['CALL_DURATION']) > 10 and x['CALL_TYPE'] == '1', calls))
            row[-1] = (len(user_outgoing_calls))
            activities_sum = sum(list(map(lambda x: int(x), row[3:])))
        elif 'Входящие звонки' in row:
            user_incoming_calls = list(filter(lambda x: x['PORTAL_USER_ID'] == user_id and x['CALL_TYPE'] == '2', calls))
            row[-1] = (len(user_incoming_calls))
            activities_sum = sum(list(map(lambda x: int(x), row[3:])))
        elif 'Отправленные письма' in row:
            user_emails = list(filter(lambda x: x['AUTHOR_ID'] == user_id, sent_email))
            row[-1] = (len(user_emails))
            activities_sum = sum(list(map(lambda x: int(x), row[3:])))
        elif 'Обращений в 1С:Коннект' in row:
            closed_user_connect_tasks = list(filter(lambda x: x['responsibleId'] == user_id and '1С:Коннект' in x['title'], tasks))
            row[-1] = (len(closed_user_connect_tasks))
            activities_sum = sum(list(map(lambda x: int(x), row[3:])))
        row.append(activities_sum)
        new_worksheet_data.append(row)
    worksheet.clear()
    worksheet.update('A1', new_worksheet_data)

    # Форматирование

    worksheet.format('A1:AI1000', {"horizontalAlignment": "CENTER", "textFormat": {"bold": False}})
    worksheet.freeze(rows=1)
    col_names = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J', 11: 'K', 12: 'L',
                 13: 'M', 14: 'N', 15: 'O', 16: 'P', 17: 'Q', 18: 'R', 19: 'S', 20: 'T', 21: 'U', 22: 'V', 23: 'W',
                 24: 'X', 25: 'Y', 26: 'Z', 27: 'AA', 28: 'AB', 29: 'AC', 30: 'AD', 31: 'AE', 32: 'AF', 33: 'AG',
                 34: 'AH', 35: 'I'}
    bold_col_number = len(new_worksheet_data[0]) - 1
    bold_col_range = f'{col_names[bold_col_number]}1:{col_names[bold_col_number]}1000'
    worksheet.format(bold_col_range, {"textFormat": {"bold": True}})


if __name__ == '__main__':
    update_user_activity_statistic()
