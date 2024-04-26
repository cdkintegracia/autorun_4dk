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


def get_tasks() -> dict:
    task_tags = ['БП', 'ЗУП']
    result = {}
    current_date = datetime.now()
    filter_date_b24_start = datetime.strftime(current_date, '%Y-%m-%d')
    filter_date_b24_end = datetime.strftime(current_date + timedelta(days=1), '%Y-%m-%d')
    result.setdefault('ЛК', {})
    tasks = b.get_all('tasks.task.list', {
            'filter': {
                'GROUP_ID': '7',
                '>=CREATED_DATE': filter_date_b24_start,
                '<CREATED_DATE': filter_date_b24_end}
        })
    result['ЛК'].setdefault('Всего ЛК', tasks)
    for tag in task_tags:
        tasks = b.get_all('tasks.task.list', {
            'filter': {
                'TAG': tag,
                '>=CREATED_DATE': filter_date_b24_start,
                '<CREATED_DATE': filter_date_b24_end}
        })
        result['ЛК'].setdefault(tag, tasks)
    tasks = b.get_all('tasks.task.list', {
        'filter': {
            'GROUP_ID': '1',
            '>=CREATED_DATE': filter_date_b24_start,
            '<CREATED_DATE': filter_date_b24_end
        }})
    result.setdefault('ТЛП', tasks)
    return result


def get_values_sum(row: list) -> str:
    values_sum = 0
    for ind in range(len(row)):
        if ind == len(row) - 1:
            break
        value = row[ind]
        if str(value).isdigit():
            values_sum += int(value)
    return str(values_sum)


def update_daily_task_statistic():
    week_day = datetime.today().isoweekday()
    if week_day in [7]:  # Выходные
        return
    tasks = get_tasks()
    file_name = f'Задачи {datetime.now().year}'
    sheet_name = month_int_names[datetime.now().month]
    try:
        google_access = gspread.service_account(f"/root/credentials/{authentication('Google')}")
    except FileNotFoundError:
        google_access = gspread.service_account(f"C:\\Users\\USER\\Documents\\GitHub\\autorun_4dk\\{authentication('Google')}")
    spreadsheet = google_access.open(file_name)
    try:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1, cols=1)
        titles = [
            ['Группа', '', 'Всего'],
            ['ЛК', ''],
            ['', 'Всего ЛК', ''],
            ['', 'БП', ''],
            ['', 'ЗУП', ''],
            [''],
            ['ТЛП', 'Всего ТЛП', ]
        ]
        worksheet.update('A1', titles)
    except gspread.exceptions.APIError:
        worksheet = spreadsheet.worksheet(sheet_name)
    worksheet_values = worksheet.get_all_values()
    new_worksheet_data = []
    for row in worksheet_values:
        print(row)
        if 'Группа' in row:
            current_date = datetime.strftime(datetime.now(), '%d.%m.%y')
            row.insert(-1, current_date)
        elif 'БП' in row:
            row.insert(-1, len(tasks['ЛК']['БП']))
        elif 'ЗУП' in row:
            row.insert(-1, len(tasks['ЛК']['ЗУП']))
        elif 'Всего ЛК' in row:
            row.insert(-1, len(tasks['ЛК']['Всего ЛК']))
            row[-1] = get_values_sum(row)
        elif 'ТЛП' in row:
            row.insert(-1, len(tasks['ТЛП']))
            row[-1] = get_values_sum(row)

        new_worksheet_data.append(row)
    worksheet.clear()
    worksheet.update('A1', new_worksheet_data)


if __name__ == '__main__':
    update_daily_task_statistic()
