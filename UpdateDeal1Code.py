from datetime import datetime
from datetime import timedelta

from fast_bitrix24 import Bitrix

from authentication import authentication


# Считывание файла authentication.txt

webhook = authentication('Bitrix')
b = Bitrix(webhook)

def update_deal_1c_code():
    deals = b.get_all('crm.deal.list', {
        'select': [
            'STAGE_ID',
            'CLOSEDATE',
            'UF_CRM_1638958630625'
        ], 'filter': {
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
            if deal['UF_CRM_1638958630625'] not in ['None', None]:
                dpo = deal['UF_CRM_1638958630625'][:10]
                if dpo == check_date and deal['STAGE_ID'] != 'C1:NEW':
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
    update_deal_1c_code()

