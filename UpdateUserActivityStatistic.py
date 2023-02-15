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
    '''
    week_day = datetime.today().isoweekday()
    if week_day in [6, 7]:  # Выходные
        return
    '''
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
    file_name = f'Активность пользователей {datetime.now().year}'
    sheet_name = month_int_names[datetime.now().month]
    try:
        google_access = gspread.service_account(f"/root/credentials/{authentication('Google')}")
    except FileNotFoundError:
        google_access = gspread.service_account(f"C:\\Users\\mok\\Documents\\GitHub\\{authentication('Google')}")
    spreadsheet = google_access.open(file_name)
    try:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1, cols=1)
        titles = [
            ['Пользователь', 'Активность', 'Всего']
        ]
        users = list(map(lambda x: [f"{x['NAME']} {x['LAST_NAME']}"], users_info))
        users = list(sorted(users, key=lambda x: x[0]))
        for user in users:
            titles.append(user)
            titles.append(['', 'Завершенные задачи'])
            titles.append(['', 'Исходящие звонки'])
            titles.append(['', 'Входящие звонки'])
            titles.append(['', 'Отправленные письма'])
            titles.append(['', 'Обращений в 1С:Коннект'])
        worksheet.update('A1', titles)
    except gspread.exceptions.APIError:
        worksheet = spreadsheet.worksheet(sheet_name)

    worksheet_values = worksheet.get_all_values()
    new_worksheet_data = []

    date_filter = datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')
    end_date_filter = datetime.strftime(datetime.now(), '%Y-%m-%d')
    calls = b.get_all('voximplant.statistic.get', {'filter': {'>=CALL_START_DATE': date_filter, 'CALL_FAILED_CODE': '200', '<CALL_START_DATE': end_date_filter}})
    sent_email = b.get_all('crm.activity.list', {'filter': {'PROVIDER_TYPE_ID': 'EMAIL', '>=CREATED': date_filter, 'DIRECTION': '2', '<CREATED': end_date_filter}})
    tasks = b.get_all('tasks.task.list', {'filter': {'>=CLOSED_DATE': date_filter, '<CLOSED_DATE': end_date_filter}})
    user_name = ''
    user_id = ''
    for row in worksheet_values:
        activities_sum = ''
        if 'Пользователь' in row:
            row.insert(-1, datetime.strftime(datetime.now() - timedelta(days=1), '%d.%m.%Y'))
        elif row[1] == '':
            user_name = row[0]
            user_id = list(filter(lambda x: x['NAME'] == user_name.split()[0] and x['LAST_NAME'] == user_name.split()[1], users_info))[0]['ID']
        elif 'Завершенные задачи' in row:
            user_closed_tasks = list(filter(lambda x: x['responsibleId'] == user_id and '1С:Коннект' not in x['title'], tasks))
            row[-1] = (len(user_closed_tasks))
            activities_sum = sum(list(map(lambda x: int(x), row[2:])))
        elif 'Исходящие звонки' in row:
            user_outgoing_calls = list(filter(lambda x: x['PORTAL_USER_ID'] == user_id and int(x['CALL_DURATION']) > 10 and x['CALL_TYPE'] == '1', calls))
            row[-1] = (len(user_outgoing_calls))
            activities_sum = sum(list(map(lambda x: int(x), row[2:])))
        elif 'Входящие звонки' in row:
            user_incoming_calls = list(filter(lambda x: x['PORTAL_USER_ID'] == user_id and x['CALL_TYPE'] == '2', calls))
            row[-1] = (len(user_incoming_calls))
            activities_sum = sum(list(map(lambda x: int(x), row[2:])))
        elif 'Отправленные письма' in row:
            user_emails = list(filter(lambda x: x['AUTHOR_ID'] == user_id, sent_email))
            row[-1] = (len(user_emails))
            activities_sum = sum(list(map(lambda x: int(x), row[2:])))
        elif 'Обращений в 1С:Коннект' in row:
            closed_user_connect_tasks = list(filter(lambda x: x['responsibleId'] == user_id and '1С:Коннект' in x['title'], tasks))
            row[-1] = (len(closed_user_connect_tasks))
            activities_sum = sum(list(map(lambda x: int(x), row[2:])))
        row.append(activities_sum)
        new_worksheet_data.append(row)
    worksheet.clear()
    worksheet.update('A1', new_worksheet_data)
