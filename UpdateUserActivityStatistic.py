from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import gspread
from fast_bitrix24 import Bitrix
from gspread.exceptions import WorksheetNotFound

from authentication import authentication


b = Bitrix(authentication('Bitrix'))

MONTH_NAMES = {
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

EXCLUDED_USER_IDS = [
    '209',   # Администратор ТЛП
    '213',   # Администратор
    '91',    # Дежурный администратор
    '235',   # Тестовый аккаунт
    '201',   # Отдел внедрения
    '173',   # Робот Задач
    '17',    # Специалист ЛК
    '113',   # Диспетчер ЛК
    '333',   # Отчет Сервисный выезд
    '59',    # Иван Иванов
    '205',   # b24_asterisk
    '139',   # Антон Степанов
    '639',   # Служба качества ЧДК
    '313',
    '297',
    '4523',
    '1427',
    '6073',
]

ACTIVITY_CLOSED_TASKS = 'Завершенные задачи'
ACTIVITY_OUTGOING_CALLS = 'Исходящие звонки'
ACTIVITY_INCOMING_CALLS = 'Входящие звонки'
ACTIVITY_SENT_EMAILS = 'Отправленные письма'
ACTIVITY_CONNECT = 'Обращений в 1С:Коннект'

ACTIVITY_NAMES = [
    ACTIVITY_CLOSED_TASKS,
    ACTIVITY_OUTGOING_CALLS,
    ACTIVITY_INCOMING_CALLS,
    ACTIVITY_SENT_EMAILS,
    ACTIVITY_CONNECT,
]


def safe_int(value) -> int:
    """
    Преобразует значение ячейки Google Sheets в целое число.
    Пустые и некорректные значения превращаются в 0.
    """
    if value in (None, ''):
        return 0

    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(str(value).replace(',', '.')))
        except (TypeError, ValueError):
            return 0


def column_number_to_name(column_number: int) -> str:
    """
    Преобразует номер столбца в буквенное обозначение Google Sheets:
    1 -> A, 26 -> Z, 27 -> AA.
    """
    result = ''

    while column_number > 0:
        column_number, remainder = divmod(column_number - 1, 26)
        result = chr(65 + remainder) + result

    return result


def get_google_client():
    """
    Ищет файл сервисного аккаунта сначала на сервере,
    затем на локальном Mac.
    """
    credentials_name = authentication('Google')

    credentials_paths = [
        Path('/root/credentials') / credentials_name,
        Path('/Users/borisishkin/Documents/GitHub/autorun_4dk')
        / credentials_name,
    ]

    for credentials_path in credentials_paths:
        if credentials_path.exists():
            return gspread.service_account(
                filename=str(credentials_path)
            )

    searched_paths = '\n'.join(
        str(path) for path in credentials_paths
    )

    raise FileNotFoundError(
        'Не найден файл доступа к Google Sheets. '
        f'Проверены пути:\n{searched_paths}'
    )


def get_department_name(user_info, departments_by_id: dict) -> str:
    """
    Возвращает название первого отдела пользователя.
    """
    user_departments = user_info.get('UF_DEPARTMENT') or []

    if not isinstance(user_departments, list):
        user_departments = [user_departments]

    if not user_departments:
        return ''

    department_id = str(user_departments[0])

    return departments_by_id.get(
        department_id,
        f'Неизвестный отдел {department_id}'
    )


def build_initial_sheet_data(users_info, departments):
    """
    Создаёт исходную структуру нового месячного листа.
    """
    rows = [
        ['Пользователь', 'Отдел', 'Активность', 'Всего']
    ]

    departments_by_id = {
        str(department.get('ID')): department.get('NAME', '')
        for department in departments
        if department.get('ID')
    }

    sorted_users = sorted(
        users_info,
        key=lambda user: (
            (user.get('LAST_NAME') or '').strip().lower(),
            (user.get('NAME') or '').strip().lower(),
            str(user.get('ID') or '').zfill(10),
        )
    )

    for user_info in sorted_users:
        first_name = (user_info.get('NAME') or '').strip()
        last_name = (user_info.get('LAST_NAME') or '').strip()
        user_id = str(user_info.get('ID') or '').strip()

        display_name = ' '.join(
            value
            for value in [first_name, last_name, user_id]
            if value
        )

        if not display_name:
            continue

        department_name = get_department_name(
            user_info,
            departments_by_id
        )

        # Строка-разделитель пользователя
        rows.append([
            display_name,
            department_name,
            '',
            '',
        ])

        for activity_name in ACTIVITY_NAMES:
            rows.append([
                display_name,
                department_name,
                activity_name,
                '',
            ])

    return rows


def extract_user_id(user_display_name: str) -> str:
    """
    Получает ID из строки вида:
    Иван Иванов 123

    Не зависит от количества слов в имени или фамилии.
    """
    value = str(user_display_name or '').strip()

    if not value:
        return ''

    user_id = value.rsplit(maxsplit=1)[-1]

    if not user_id.isdigit():
        print(
            'Не удалось определить ID пользователя из строки: '
            f'{user_display_name!r}'
        )
        return ''

    return user_id


def collect_activity_statistics(tasks, calls, sent_email):
    """
    Считает активности по каждому пользователю.
    """
    statistics = {
        ACTIVITY_CLOSED_TASKS: defaultdict(int),
        ACTIVITY_OUTGOING_CALLS: defaultdict(int),
        ACTIVITY_INCOMING_CALLS: defaultdict(int),
        ACTIVITY_SENT_EMAILS: defaultdict(int),
        ACTIVITY_CONNECT: defaultdict(int),
    }

    for task in tasks:
        user_id = str(
            task.get('responsibleId')
            or task.get('RESPONSIBLE_ID')
            or ''
        )

        title = str(
            task.get('title')
            or task.get('TITLE')
            or ''
        )

        if not user_id:
            continue

        if '1С:Коннект' in title:
            statistics[ACTIVITY_CONNECT][user_id] += 1
        else:
            statistics[ACTIVITY_CLOSED_TASKS][user_id] += 1

    for call in calls:
        user_id = str(call.get('PORTAL_USER_ID') or '')

        if not user_id:
            continue

        call_type = str(call.get('CALL_TYPE') or '')
        call_duration = safe_int(call.get('CALL_DURATION'))

        if call_type == '1' and call_duration > 10:
            statistics[ACTIVITY_OUTGOING_CALLS][user_id] += 1

        elif call_type == '2':
            statistics[ACTIVITY_INCOMING_CALLS][user_id] += 1

    for email in sent_email:
        user_id = str(email.get('AUTHOR_ID') or '')

        if user_id:
            statistics[ACTIVITY_SENT_EMAILS][user_id] += 1

    return statistics


def update_user_activity_statistic():
    now = datetime.now()

    # Суббота и воскресенье
    if now.isoweekday() in (6, 7):
        print('Сегодня выходной. Скрипт завершён.')
        return

    print('Получаем пользователей Битрикс24...')

    users_info = b.get_all(
        'user.get',
        {
            'filter': {
                '!ID': EXCLUDED_USER_IDS,
                'ACTIVE': 'true',
            }
        }
    )

    print('Получаем отделы Битрикс24...')

    departments = b.get_all('department.get')

    file_name = f'Активность пользователей {now.year}'
    sheet_name = MONTH_NAMES[now.month]

    google_access = get_google_client()
    spreadsheet = google_access.open(file_name)

    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        print(f'Лист «{sheet_name}» найден.')

    except WorksheetNotFound:
        print(f'Создаём лист «{sheet_name}»...')

        worksheet = spreadsheet.add_worksheet(
            title=sheet_name,
            rows=1000,
            cols=36,
        )

    worksheet_values = worksheet.get_all_values()

    # Проверяем не только наличие строк,
    # но и наличие хотя бы одной непустой ячейки.
    sheet_has_data = any(
        any(str(cell).strip() for cell in row)
        for row in worksheet_values
    )

    # Лист мог быть создан предыдущим неудачным запуском,
    # но остаться фактически пустым.
    if not sheet_has_data:
        print('Лист пуст. Заполняем структуру нового листа...')

        initial_data = build_initial_sheet_data(
            users_info,
            departments,
        )

        if not initial_data or len(initial_data) <= 1:
            raise RuntimeError(
                'Не удалось сформировать список пользователей '
                'для нового листа.'
            )

        worksheet.clear()

        worksheet.update(
            range_name='A1',
            values=initial_data,
        )

        worksheet_values = initial_data

        print(
            f'Создано строк: {len(initial_data)}, '
            f'пользователей: {(len(initial_data) - 1) // 6}'
        )

    date_filter = now.strftime('%Y-%m-%d')
    end_date_filter = (
        now + timedelta(days=1)
    ).strftime('%Y-%m-%d')

    print('Получаем звонки...')

    calls = b.get_all(
        'voximplant.statistic.get',
        {
            'filter': {
                '>=CALL_START_DATE': date_filter,
                '<CALL_START_DATE': end_date_filter,
                'CALL_FAILED_CODE': '200',
            }
        }
    )

    print('Получаем отправленные письма...')

    sent_email = b.get_all(
        'crm.activity.list',
        {
            'filter': {
                'PROVIDER_TYPE_ID': 'EMAIL_COMPRESSED',
                '>=CREATED': date_filter,
                '<CREATED': end_date_filter,
                'DIRECTION': '2',
            }
        }
    )

    print('Получаем завершённые задачи...')

    tasks = b.get_all(
        'tasks.task.list',
        {
            'filter': {
                '>=CLOSED_DATE': date_filter,
                '<CLOSED_DATE': end_date_filter,
            }
        }
    )

    statistics = collect_activity_statistics(
        tasks=tasks,
        calls=calls,
        sent_email=sent_email,
    )

    # Google Sheets может не возвращать пустые ячейки
    # в конце строки. Поэтому определяем общую ширину.
    worksheet_width = max(
        4,
        max(len(row) for row in worksheet_values),
    )

    new_worksheet_data = []
    current_user_id = ''
    current_date = now.strftime('%d.%m.%Y')

    for original_row in worksheet_values:
        row = list(original_row)

        # Дополняем короткие строки пустыми ячейками.
        if len(row) < worksheet_width:
            row.extend(
                [''] * (worksheet_width - len(row))
            )

        # Полностью пустые строки не нужны.
        if not any(str(cell).strip() for cell in row):
            continue

        # Заголовок таблицы
        if row[0] == 'Пользователь':
            # Добавляем дату перед столбцом «Всего».
            row.insert(len(row) - 1, current_date)
            new_worksheet_data.append(row)
            continue

        activity_name = str(row[2] or '').strip()

        # Строка-разделитель пользователя
        if not activity_name:
            current_user_id = extract_user_id(row[0])

            # Добавляем пустую ячейку для сегодняшней даты
            # перед столбцом «Всего».
            row.insert(len(row) - 1, '')

            new_worksheet_data.append(row)
            continue

        # Строка с конкретной активностью
        if (
            current_user_id
            and activity_name in statistics
        ):
            current_value = statistics[
                activity_name
            ][current_user_id]

            # Последняя ячейка до обработки — старое «Всего».
            # Заменяем её сегодняшним значением.
            row[-1] = current_value

            # Теперь row[3:] содержит значения по всем датам,
            # включая сегодняшнее.
            total_value = sum(
                safe_int(value)
                for value in row[3:]
            )

            # Добавляем новый итог.
            row.append(total_value)

        else:
            # Неизвестная строка: просто добавляем пустую
            # ячейку для новой даты перед итогом.
            row.insert(len(row) - 1, '')

        new_worksheet_data.append(row)

    if not new_worksheet_data:
        raise RuntimeError(
            f'Не удалось сформировать данные для листа '
            f'«{sheet_name}».'
        )

    print('Записываем данные в Google Sheets...')

    worksheet.clear()

    worksheet.update(
        range_name='A1',
        values=new_worksheet_data,
    )

    # Форматирование
    row_count = len(new_worksheet_data)
    column_count = len(new_worksheet_data[0])
    last_column_name = column_number_to_name(column_count)

    worksheet.format(
        f'A1:{last_column_name}{row_count}',
        {
            'horizontalAlignment': 'CENTER',
            'textFormat': {
                'bold': False,
            },
        },
    )

    worksheet.freeze(rows=1)

    # Последний столбец — «Всего».
    worksheet.format(
        f'{last_column_name}1:{last_column_name}{row_count}',
        {
            'textFormat': {
                'bold': True,
            }
        },
    )

    print(
        f'Готово. Лист «{sheet_name}» обновлён. '
        f'Дата: {current_date}.'
    )


if __name__ == '__main__':
    update_user_activity_statistic()