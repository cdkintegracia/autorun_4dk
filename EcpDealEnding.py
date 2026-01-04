from datetime import datetime, timedelta

from fast_bitrix24 import Bitrix

from authentication import authentication


b = Bitrix(authentication('Bitrix'))


def ecp_deal_ending():
    if datetime.now().weekday() in [5, 6]:
        return 
    date_pattern = '%Y-%m-%d'
    if datetime.now().weekday() != 0:
        filter_date_start = (datetime.now() + timedelta(days=6)).strftime(date_pattern)
        filter_date_end = (datetime.now() + timedelta(days=8)).strftime(date_pattern)
        task_text = (datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y")
    else:
        filter_date_start = (datetime.now() + timedelta(days=4)).strftime(date_pattern)
        filter_date_end = (datetime.now() + timedelta(days=8)).strftime(date_pattern)
        task_text = f'{(datetime.now() + timedelta(days=5)).strftime("%d.%m.%Y")} - {(datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y")}'
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

    if deals:
        task = b.call('tasks.task.add', {
            'fields': {
                'TITLE': f'Напомните клиентам о продлении ЭЦП {task_text}',
                'GROUP_ID': '11',
                'CREATED_BY': '173',
                'RESPONSIBLE_ID': '173',
                'DESCRIPTION': f'Дата окончания ЭЦП: {task_text}',
            }
        }, raw=True)['result']['task']['id']

        for deal in deals:
            company_name = list(filter(lambda x: x['ID'] == deal['COMPANY_ID'], companies))[0]['TITLE']
            check_box_text = f'{company_name}. {deal["TITLE"]}: https://vc4dk.bitrix24.ru/crm/deal/details/{deal["ID"]}/\n'
            b.call('task.checklistitem.add', [task, {'TITLE': check_box_text}], raw=True)


if __name__ == '__main__':
    ecp_deal_ending()