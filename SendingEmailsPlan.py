from datetime import datetime, timedelta

from fast_bitrix24 import Bitrix
import requests

from authentication import authentication
from web_app_ip import web_app_ip


b = Bitrix(authentication('Bitrix'))


def sending_emails_plan():
    if datetime.now().weekday() in [5, 6]:
        return
    start_date_filter = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    if datetime.now().weekday() == 4:
        end_date_filter = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    else:
        end_date_filter = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    deals = b.get_all('crm.deal.list', {
        'filter': {
            '>CLOSEDATE': start_date_filter,
            '<CLOSEDATE': end_date_filter,
            'CATEGORY_ID': '1',
            '!TYPE_ID': [
                'UC_QQPYF0',       # Лицензия
                'UC_O99QUW',       # Отчетность
                'UC_OV4T7K',       # Отчетность (в рамках ИТС)
            ],
            '!ASSIGNED_BY_ID': '93',

        }
    })
    companies = b.get_all('crm.company.list', {
        'filter': {
            'ID': list(map(lambda x: x['COMPANY_ID'], deals))
        }
    })
    texts_and_users = {}
    for deal in deals:
        company = list(filter(lambda x: x['ID'] == deal['COMPANY_ID'], companies))[0]
        message_text = f'Внимание! У клиента {company["TITLE"]} {datetime.fromisoformat(deal["CLOSEDATE"]).strftime("%d.%m.%Y")} заканчивается оплата по договору {deal["TITLE"]}. Пожалуйста, свяжитесь с клиентом.\n'
        texts_and_users[deal['ASSIGNED_BY_ID']] = texts_and_users.get(deal['ASSIGNED_BY_ID'], '') + message_text

    for user, text in texts_and_users.items():
        data = {
            'job': 'send_message',
            'dialog_id': user,
            'message': text,
        }
        requests.post(url=f'{web_app_ip}/bitrix/chat_bot', json=data)
