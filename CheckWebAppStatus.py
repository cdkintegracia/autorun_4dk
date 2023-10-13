import requests
from requests import request
from fast_bitrix24 import Bitrix
from authentication import authentication
from web_app_ip import web_app_ip


try:
    r = request(method='GET', url=web_app_ip)
    with open('/root/autorun_4dk/status_web_app.txt', 'r') as file:
        status = file.read().split(': ')[-1]
    if status == 'offline':
        with open('/root/autorun_4dk/status_web_app.txt', 'w') as file:
            file.write('Status_web_app: online')
except requests.ConnectionError:
    with open('/root/autorun_4dk/status_web_app.txt', 'r') as file:
        status = file.read().split(': ')[-1]
    if status == 'online':
        with open('/root/autorun_4dk/status_web_app.txt', 'w') as file:
            file.write('Status_web_app: offline')

        b = Bitrix(authentication('Bitrix'))
        notification_users = ['1', '311']
        for user in notification_users:
            data = {
                'BOT_ID': '1019',
                'CLIENT_ID': '0ygqrhrjjhasn7uap3ginxcvuio3h99o',
                'DIALOG_ID': user,
                'MESSAGE': 'Работа веб-приложения остановлена',
            }

            r = requests.post(url=f'{authentication("Chat-bot").strip()}imbot.message.add', json=data)
            print(r.text())

        '''
        b = Bitrix(authentication('Bitrix'))
        b.call('tasks.task.add', {
            'fields': {
                'RESPONSIBLE_ID': '311',
                'AUDITORS': '1',
                'GROUP_ID': '13',
                'TITLE': 'Работа веб-приложения остановлена',
                'CREATED_BY': '173',
            }
        })
        '''

