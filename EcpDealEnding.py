from datetime import datetime, timedelta

from fast_bitrix24 import Bitrix

from authentication import authentication


b = Bitrix(authentication('Bitrix'))


def ecp_deal_ending():
    date_pattern = '%Y-%m-%d'
    filter_date_start = (datetime.now() + timedelta(days=6)).strftime(date_pattern)
    filter_date_end = (datetime.now() + timedelta(days=8)).strftime(date_pattern)
    deals = b.get_all('crm.deal.list', {
        'select': ['*', 'UF_*'],
        'filter': {
            '>UF_CRM_1637934330556': filter_date_start,
            '<UF_CRM_1637934330556': filter_date_end,
            'TYPE_ID': ['UC_O99QUW', 'UC_OV4T7K'],
            '!STAGE_ID': ['C1:WON', 'C1:LOSE']
        }
    })
    companies = b.get_all('crm.company.list', {
        'filter': {
            'ID': list(map(lambda x: x['COMPANY_ID'], deals))
        }
    })

    task_text = ''
    for index, deal in enumerate(deals, 1):
        if index == 1:
            task_text += f'Напомните клиентам о продлении ЭЦП\n' \
                         f'Дата окончания ЭЦП: {(datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y")}\n\n'
        company_name = list(filter(lambda x: x['ID'] == deal['COMPANY_ID'], companies))[0]['TITLE']
        task_text += f'{index}. {company_name} https://vc4dk.bitrix24.ru/crm/deal/details/{deal["ID"]}/\n'

    if task_text:
        b.call('tasks.task.add', {
            'fields': {
                'TITLE': f'Напомните клиентам о продлении ЭЦП {(datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y")}',
                'GROUP_ID': '11',
                'CREATED_BY': '173',
                'RESPONSIBLE_ID': '91',
                'DESCRIPTION': task_text,
            }
        })



if __name__ == '__main__':
    ecp_deal_ending()