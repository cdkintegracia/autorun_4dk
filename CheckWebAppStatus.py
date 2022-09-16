import requests
from requests import request
from fast_bitrix24 import Bitrix
from authentication import authentication

try:
    r = request(method='GET', url='http://141.8.195.67:5000')
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
        b.call('tasks.task.add', {
            'fields': {
                'RESPONSIBLE_ID': '311',
                'AUDITORS': '1',
                'GROUP_ID': '13',
                'TITLE': 'Работа веб-приложения остановлена',
                'CREATED_BY': '173',
            }
        })

