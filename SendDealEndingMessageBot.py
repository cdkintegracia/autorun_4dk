from datetime import datetime, timedelta

from fast_bitrix24 import Bitrix
import requests

from authentication import authentication
from web_app_ip import web_app_ip


b = Bitrix(authentication('Bitrix'))


def main(days):
    filter_date = datetime.now() + timedelta(days=days)
    if days == 39:
        deals = b.get_all('crm.deal.list', {
            'filter': {
                'CLOSEDATE': filter_date.strftime('%Y-%m-%d 00:00:00'),
                '!TYPE_ID': ['UC_QQPYF0', 'UC_YIAJC8', 'UC_2B0CK2', 'UC_OV4T7K', 'UC_IV3HX1'],
                '!STAGE_ID': ['C1:WON', 'C1:LOSE', 'C1:UC_3J0IH6'],
                '!ASSIGNED_BY_ID': ['91', '213'],
            },
            'select': ['ASSIGNED_BY_ID', 'COMPANY_ID', 'CLOSEDATE', 'TITLE']
        })
        companies = b.get_all('crm.company.list', {
            'filter': {
                'ID': list(set(map(lambda x: x['COMPANY_ID'], deals)))
            },
            'select': ['TITLE']
        })
    else:
        deals = b.get_all('crm.deal.list', {
            'filter': {
                'CLOSEDATE': filter_date.strftime('%Y-%m-%d 00:00:00'),
                '!TYPE_ID': ['UC_QQPYF0', 'UC_YIAJC8', 'UC_2B0CK2', 'UC_OV4T7K', 'UC_IV3HX1'],
                'STAGE_ID': ['C1:NEW'],
                '!ASSIGNED_BY_ID': ['91', '213'],
            },
            'select': ['ASSIGNED_BY_ID', 'COMPANY_ID', 'CLOSEDATE', 'TITLE']
        })
        companies = b.get_all('crm.company.list', {
            'filter': {
                'ID': list(set(map(lambda x: x['COMPANY_ID'], deals)))
            },
            'select': ['TITLE']
        })
    users = set(map(lambda x: x['ASSIGNED_BY_ID'], deals))
    for user in users:
        info_text = ''
        user_deals = list(filter(lambda x: x['ASSIGNED_BY_ID'] == user, deals))
        for deal in user_deals:
            company_name = list(filter(lambda x: x['ID'] == deal['COMPANY_ID'], companies))[0]['TITLE']
            closedate = datetime.fromisoformat(deal['CLOSEDATE']).strftime('%d.%m.%Y')
            if days == 39:
                info_text += f"Сделка {deal['TITLE']} компании {company_name} завершается {closedate}. Начните работу по продлению сделки. Ссылка на сделку: https://vc4dk.bitrix24.ru/crm/deal/details/{deal['ID']}/\n\n"
            else:
                info_text += f"Сделка {deal['TITLE']} компании {company_name} завершается {closedate}. Осталось {days} дней. Начните работу по продлению сделки. Ссылка на сделку: https://vc4dk.bitrix24.ru/crm/deal/details/{deal['ID']}/\n\n"
        data = {
            'job': 'send_message',
            'dialog_id': user,
            'message': info_text
        }
        requests.post(url=f'{web_app_ip}/bitrix/chat_bot', json=data)


def send_deal_ending_message_bot():
    days_list = [39, 25, 10]
    for days in days_list:
        main(days)


if __name__ == '__main__':
    send_deal_ending_message_bot()
