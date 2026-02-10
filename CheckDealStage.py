from datetime import datetime
from datetime import timedelta

from fast_bitrix24 import Bitrix
from SendNotification import send_notification

from authentication import authentication


# Считывание файла authentication.txt

webhook = authentication('Bitrix')
b = Bitrix(webhook)

def check_deal_stage():
    deals = b.get_all('crm.deal.list', {
        'select': [
            'STAGE_ID',
            'CLOSEDATE',
            'UF_CRM_1638958630625',
            'TYPE_ID',
        ], 'filter': {
            '!TYPE_ID': ['UC_QQPYF0', 'UC_YIAJC8'],  # != Лицензия, Лицензия с купоном ИТС 2024-10-28 САА
            'STAGE_ID': [
                'C1:NEW',
                'C1:UC_0KJKTY',
                'C1:UC_3J0IH6',
            ],
            'CATEGORY_ID': '1',
        }})
    previous_date = datetime.now() - timedelta(days=1)
    check_date = datetime.strftime(previous_date, "%Y-%m-%d")

    for deal in deals:
        if 'UF_CRM_1638958630625' in deal:
            if deal['UF_CRM_1638958630625'] not in ['None', None, '']:
                dpo = deal['UF_CRM_1638958630625'][:10]
                # Отдельное условие для Спарков
                if (dpo == check_date and deal['STAGE_ID'] != 'C1:NEW') or (dpo == check_date and deal['TYPE_ID'] in ['UC_2B0CK2', 'UC_86JXH1', 'UC_WUGAZ7']):
                    b.call('crm.deal.update', {'ID': deal['ID'], 'fields': {'STAGE_ID': 'C1:UC_KZSOR2'}})
            else:
                dk = deal['CLOSEDATE'][:10]
                if dk == check_date:
                    b.call('crm.deal.update', {'ID': deal['ID'], 'fields': {'STAGE_ID': 'C1:UC_KZSOR2'}})
        else:
            dk = deal['CLOSEDATE'][:10]
            if dk == check_date:
                b.call('crm.deal.update', {'ID': deal['ID'], 'fields': {'STAGE_ID': 'C1:UC_KZSOR2'}})


if __name__ == '__main__':
    try:
        check_deal_stage()
    except:
        send_notification(['1', '1391'], 'Работа ночных процессов прервана на актуализации стадий сделок')

