from fast_bitrix24 import Bitrix
import gspread

from authentication import authentication


def main():
    """
    Bitrix
    """

    # Считывание файла authentication.txt

    webhook = authentication('Bitrix')
    b = Bitrix(webhook)

    tasks = b.get_all('bizproc.task.list', {
        'select': [
            'NAME',
            'USER_ID',
            'WORKFLOW_STARTED',
        ],
        'filter': {
            'STATUS': '0'
        }
    }
                      )
    print(tasks)
    # Поиск имени и фамилии по ID

    user_names = {}
    for task in tasks:
        if task['USER_ID'] not in user_names:
            user = b.call('user.get', {'ID': task['USER_ID']})
            user_names.setdefault(task['USER_ID'], user['NAME'] + ' ' + user['LAST_NAME'])

    titles = []
    for key in tasks[0].keys():
        if key == 'ENTITY':
            continue
        titles.append(key)


    tasks_data = list(map(lambda x: [x['DOCUMENT_ID'],
                                     x['NAME'],
                                     user_names[x['USER_ID']],
                                     x['WORKFLOW_STARTED'][:10].replace('-', '.'),
                                     'https://vc4dk.bitrix24.ru' + x['DOCUMENT_URL']], tasks))
    tasks_data.insert(0, titles)


    """
    Google sheets
    """

    access = gspread.service_account(filename=authentication('Google Data Studio'))
    spreadsheet = access.open('bitrix_data')
    worksheet = spreadsheet.worksheet('bp_tasks')

    worksheet.clear()
    worksheet.update('A1', tasks_data)

if __name__ == '__main__':
    main()


