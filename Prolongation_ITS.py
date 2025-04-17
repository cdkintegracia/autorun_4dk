from time import strftime
from calendar import monthrange
from datetime import datetime

from fast_bitrix24 import Bitrix

from authentication import authentication

# Считывание файла authentication.txt

b = Bitrix(authentication('Bitrix'))


def prolongation_its():
    #if datetime.now().day != 1:
        #return
    users = b.get_all('user.get', {'filter': {'UF_DEPARTMENT': '225'}})
    users_id = list(map(lambda x: x['ID'], users))
    users_id.append('109')

    month = '05'
    #month = strftime('%m')
    year = strftime('%Y')
    next_month = int(month) + 1
    next_year = int(year)
    if next_month > 12:
        next_month = 1
        next_year += 1
    first_date = f"{year}-{month}-01"
    second_date = f"{year}-{month}-{monthrange(int(year), int(month))[1]}"
    third_date = f"{next_year}-{next_month:02d}-{monthrange(int(next_year), int(next_month))[1] - 1}"
    print(first_date)
    print(second_date)
    print(third_date)
    
    deals_main = b.get_all('crm.deal.list',
                               {'select': [
                                   'COMPANY_ID',
                                   'TITLE',
                                   'ID',
                                   'ASSIGNED_BY_ID',
                                   'TYPE_ID',
                               ], 'filter': {
                                   'ASSIGNED_BY_ID': users_id,
                                   '<=CLOSEDATE': first_date,
                                   '>=CLOSEDATE': second_date,
                                   '!TYPE_ID': ['UC_QQPYF0', 'UC_YIAJC8'],  # != Лицензия, Лицензия с купоном ИТС
                                    'CATEGORY_ID': '1',
                                   '!STAGE_ID': ['C1:WON', 'C1:LOSE'],
                               }
                               }
                               )
    
    deals_sub = b.get_all('crm.deal.list',
                               {'select': [
                                   'COMPANY_ID',
                                   'TITLE',
                                   'ID',
                                   'ASSIGNED_BY_ID',
                                   'TYPE_ID',
                               ], 'filter': {
                                   'ASSIGNED_BY_ID': users_id,
                                   '<=UF_CRM_1638958630625': second_date,
                                   '>=UF_CRM_1638958630625': third_date,
                                   '!TYPE_ID': ['UC_QQPYF0', 'UC_YIAJC8'],  # != Лицензия, Лицензия с купоном ИТС
                                   'CATEGORY_ID': '1',
                                   '!STAGE_ID': ['C1:WON', 'C1:LOSE'],
                               }
                               }
                               )                           
    '''
    deals = []
    for deal in deals_main:
        deals.append(deal)
    for deal in deals_sub:
        if deal not in deals:
            deals.append(deal)
    '''
    
    for deal in deals_main:
        company_name = b.get_all('crm.company.list', {'filter': {'ID': deal['COMPANY_ID']}})[0]['TITLE']
        b.call('tasks.task.add', {
            'fields':{
                'TITLE': f'Продление сделки {company_name}',
                'GROUP_ID': '179',
                'CREATED_BY': '173',
                'RESPONSIBLE_ID': '1391',
                'DEADLINE': second_date,
            }
        }
               )
    '''    
    for deal in deals_sub:
        if deal not in deals_main:
            company_name = b.get_all('crm.company.list', {'filter': {'ID': deal['COMPANY_ID']}})[0]['TITLE']
            b.call('tasks.task.add', {
                'fields':{
                    'TITLE': f'Продление сделки {company_name}',
                    'GROUP_ID': '179',
                    'CREATED_BY': '173',
                    'RESPONSIBLE_ID': '1391',
                    #'RESPONSIBLE_ID': deal['ASSIGNED_BY_ID'],
                    'DEADLINE': third_date,
                    #'UF_CRM_TASK': ['D_' + deal['ID'], 'CO_' + deal['COMPANY_ID']],
                }
            }
                    )
    '''     
        
    users_id_notification = ['1391']
    #users_id_notification = ['1', '109']
    for user_id in users_id_notification:
        b.call('im.notify.system.add', {
            'USER_ID': user_id,
            'MESSAGE': 'Задачи на продление ИТС созданы'})

if __name__ == '__main__':
    prolongation_its()