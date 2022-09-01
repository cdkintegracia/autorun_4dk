from fast_bitrix24 import Bitrix
import gspread

from authentication import authentication


def main():

    """
    Bitrix
    """

    # Считывание файла authentication.txt

    webhook = authentication('Bitrix')
    #webhook = 'https://vc4dk.bitrix24.ru/rest/311/r1oftpfibric5qym/'
    b = Bitrix(webhook)

    tasks = b.get_all('bizproc.task.list', {
        'select': [
            'NAME',
            'USER_ID',
            'WORKFLOW_STARTED',
            'ID',
        ],
        'filter': {
            'STATUS': '0'
        }
    }
                      )

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

    bitrix_methods = {
        'type': 1,
        'deal': 2,
        'company': 3,
    }

    tasks_data = list(map(lambda x: [x['DOCUMENT_ID'],
                                     x['NAME'],
                                     user_names[x['USER_ID']],
                                     x['WORKFLOW_STARTED'][:10].replace('-', '.'),
                                     f'https://vc4dk.bitrix24.ru/company/personal/bizproc/{x["ID"]}/?back_url=%2Fcompany%2Fpersonal%2Fbizproc%2F&USER_ID={x["USER_ID"]}',
                                     'https://vc4dk.bitrix24.ru' + x['DOCUMENT_URL'],
                                     ],
                          tasks))
    tasks_data.insert(0, titles)


    """
    Google sheets
    """

    access = gspread.service_account(filename=f"/root/autorun_4dk/credentials/{authentication('Google Data Studio')}")
    #access = gspread.service_account(filename='bitrix24-data-studio-2278c7bfb1a7.json')
    spreadsheet = access.open('bitrix_data')
    worksheet = spreadsheet.worksheet('bp_tasks')

    worksheet.clear()
    worksheet.update('A1', tasks_data)

if __name__ == '__main__':
    main()


