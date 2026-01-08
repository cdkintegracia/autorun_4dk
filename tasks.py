import time
from datetime import datetime
from datetime import timedelta
from calendar import monthrange

from fast_bitrix24 import Bitrix
from authentication import authentication


# Считывание файла authentication.txt

webhook = authentication('Bitrix')

b = Bitrix(webhook)


def create_sub_task(main_task_id: str, deal_name, company_name, deal_id, task_type: str, company_id: str):

    task_type_description = {
        'ДК': 'Дата завершения',
        'ДПО': 'Дата проверки оплаты'
    }

    b.call('tasks.task.add', {
        'fields': {
            'TITLE': f"Что делать со сделкой {deal_name} {company_name}",
            'DESCRIPTION': f"Сегодня, {time.strftime('%d.%m.%Y')} - {task_type_description[task_type]} для {deal_name}. Свяжитесь с менеджером или с клиентом и укажите в комментарии к задаче, что нужно сделать с сделкой",
            'DEADLINE': time.strftime('%d.%m.%Y') + ' ' + '17:00',
            'RESPONSIBLE_ID': '173',
            'PARENT_ID': main_task_id,
            'UF_CRM_TASK': [f"D_{deal_id}", f"CO_{company_id}"],
            'GROUP_ID': '77',
            'CREATED_BY': '173'
        }})


def create_check_list(data: dict, main_task_id: str, task_type: str, check_list_name: str):
    if not data:
        return
    '''
    main_checklist = b.call('task.checklistitem.add', [
        main_task_id, {
            # <Название компании> <Название сделки> <Ссылка на сделку>
            'TITLE': check_list_name, 'PARENT_ID': main_task_id,
        }
    ], raw=True
                            )
    '''
    main_checklist = b.call('task.checklistitem.add', {
        'taskId': int(main_task_id),
        'FIELDS': {
            'TITLE': check_list_name,
        }
    }, raw=True)

    for deal_id in data:
        '''
        b.call('task.checklistitem.add', [
            main_task_id, {
                'TITLE': f"{data[deal_id][0]} - {data[deal_id][1]} https://vc4dk.bitrix24.ru/crm/deal/details/{deal_id}/",
                'PARENT_ID': main_checklist['result'],
            }
        ], raw=True
               )
        '''
        print(f"{data[deal_id][0]} - {data[deal_id][1]} https://vc4dk.bitrix24.ru/crm/deal/details/{deal_id}/")
        print(main_checklist['result'])
        b.call('task.checklistitem.add', {
            'taskId': main_task_id,
            'FIELDS': {
                'TITLE': f"{data[deal_id][0]} - {data[deal_id][1]} https://vc4dk.bitrix24.ru/crm/deal/details/{deal_id}/",
                'PARENT_ID': main_checklist['result'],
            }
        }, raw=True)
        create_sub_task(main_task_id, data[deal_id][0], data[deal_id][1], deal_id, task_type, data[deal_id][2])


def create_task(deals, task_type):

    task_types = {
        'ДК': 'Эти сделки завершаются',
        'ДПО': 'Внимание! Наступила дата проверки оплаты для сделок'
    }

    autoprolongation_deals = {}
    no_autoprolongation_deals = {}

    for deal in deals:

        # Получение названия компании
        company = b.get_all('crm.company.list', {'filter': {'ID': deal['COMPANY_ID']}})[0]

        # Формирование массива для чек-листа, подзадач
        if deal['UF_CRM_1637933869479'] == '0':
            no_autoprolongation_deals.setdefault(deal['ID'], [deal['TITLE'], company['TITLE'], deal['COMPANY_ID']])
        else:
            autoprolongation_deals.setdefault(deal['ID'], [deal['TITLE'], company['TITLE'], deal['COMPANY_ID']])

    # Создание задачи

    time_task = time.strftime('%d.%m.%Y')  # Время для названия задачи

    if autoprolongation_deals or no_autoprolongation_deals:
        week_day = datetime.today().isoweekday()
        if week_day != 5:  # Пятница
            task_title = f'{task_types[task_type]} ({time_task})'
        else:
            end_time_task = datetime.today() + timedelta(days=2)
            end_time_task = end_time_task.strftime('%d.%m.%Y')
            task_title = f"{task_types[task_type]} {time_task} - {end_time_task}"
        task = b.call('tasks.task.add', {'fields': {
            'TITLE': task_title,
            'GROUP_ID': '11',
            'RESPONSIBLE_ID': '173',
            'CREATED_BY': '173',

        }
        }, raw=True
               )['result']

        create_check_list(no_autoprolongation_deals, task['task']['id'], task_type, 'Сделки без автопролонгации')
        create_check_list(autoprolongation_deals, task['task']['id'], task_type, 'Сделки с автопролонгацией')


def main():
    # Проверка на последний день месяца
    current_day = datetime.now().day
    current_month = datetime.now().month
    current_year = datetime.now().year
    last_day_current_month = monthrange(current_year, current_month)[1]
    if current_day == last_day_current_month:
        return

    week_day = datetime.today().isoweekday()
    if week_day in [6, 7]:  # Выходные
        return
    time_filter = time.strftime('%Y-%m-%d')     # Время для фильтра в битриксе
    date_end_filter = datetime.today() + timedelta(days=2)
    date_end_filter_str = date_end_filter.strftime('%Y-%m-%d')

    #ibs >
    no_weekend = False #>ibs предупреждаем создание задач, если на выходные приходится конец месяца
    date_end_filter_before = datetime.today() + timedelta(days=1)
    date_end_filter_before_str = date_end_filter_before.strftime('%Y-%m-%d')
    if str(last_day_current_month) in date_end_filter_str or str(last_day_current_month) in date_end_filter_before_str:
        no_weekend = True
    if week_day != 5 or no_weekend == True:  # Не Пятница ИЛИ пятница, но на выходных - конец месяца

        # Сделки ДК == сегодня
        deals_dk = b.get_all('crm.deal.list', {
        'select': [
            'TITLE',
            'TYPE_ID',
            'STAGE_ID',
            'CLOSEDATE',
            'COMPANY_ID',
            'CLOSED',
            'CATEGORY_ID',
            'UF_CRM_1638958630625',
            'UF_CRM_1637933869479',
        ],
        'filter': {
            'CLOSEDATE': time_filter,   # Дата завершения == текущая дата
            '!TYPE_ID': [
                'UC_QQPYF0',    # Лицензия
                'UC_OV4T7K',    # Отчетность (в рамках ИТС)
                'UC_YIAJC8',    # Лицензия с купоном ИТС
                'UC_74DPBQ',     # Битрикс24
                #ИБС убираем КП и Фреши, согласно задаче 507278
                'UC_HT9G9H', # 'ПРОФ Земля',
                'UC_XIYCTV', # 'ПРОФ Земля+Помощник',
                'UC_N113M9', # 'ПРОФ Земля+Облако',
                'UC_5T4MAW', # 'ПРОФ Земля+Облако+Помощник',
                'UC_ZKPT1B', # 'ПРОФ Облако',
                'UC_2SJOEJ', # 'ПРОФ Облако+Помощник',
                'UC_81T8ZR', # 'АОВ',
                'UC_SV60SP', # 'АОВ+Облако',
                'UC_92H9MN', # 'Индивидуальный',
                'UC_7V8HWF', # 'Индивидуальный+Облако',
                'UC_AVBW73', # 'Базовый Земля',
                'UC_GPT391', # 'Базовый Облако',
                'UC_1UPOTU', # 'ИТС Бесплатный',
                'UC_K9QJDV', # 'ГРМ Бизнес',
                'GOODS', # 'ГРМ',
                'UC_J426ZW', # 'Садовод',
                'UC_DBLSP5', # 'Садовод+Помощник',
                '9',# 'БизнесСтарт',

            ],
            'CLOSED': 'N',  # Сделка не закрыта
            'CATEGORY_ID': '1',
        }
        }
                      )

        # Сделки ДПО == сегодня
        deals_dpo = b.get_all('crm.deal.list', {
            'select': [
                'TITLE',
                'TYPE_ID',
                'STAGE_ID',
                'CLOSEDATE',
                'COMPANY_ID',
                'CLOSED',
                'CATEGORY_ID',
                'UF_CRM_1638958630625',
                'UF_CRM_1637933869479',
            ],
            'filter': {
                'UF_CRM_1638958630625': time_filter,  # ДПО == текущая дата
                '!TYPE_ID': [
                    'UC_QQPYF0',  # Лицензия
                    'UC_OV4T7K',  # Отчетность (в рамках ИТС)
                    'UC_YIAJC8',  # Лицензия с купоном ИТС
                    'UC_74DPBQ',  # Битрикс24
                    # ИБС убираем КП и Фреши, согласно задаче 507278
                    'UC_HT9G9H',  # 'ПРОФ Земля',
                    'UC_XIYCTV',  # 'ПРОФ Земля+Помощник',
                    'UC_N113M9',  # 'ПРОФ Земля+Облако',
                    'UC_5T4MAW',  # 'ПРОФ Земля+Облако+Помощник',
                    'UC_ZKPT1B',  # 'ПРОФ Облако',
                    'UC_2SJOEJ',  # 'ПРОФ Облако+Помощник',
                    'UC_81T8ZR',  # 'АОВ',
                    'UC_SV60SP',  # 'АОВ+Облако',
                    'UC_92H9MN',  # 'Индивидуальный',
                    'UC_7V8HWF',  # 'Индивидуальный+Облако',
                    'UC_AVBW73',  # 'Базовый Земля',
                    'UC_GPT391',  # 'Базовый Облако',
                    'UC_1UPOTU',  # 'ИТС Бесплатный',
                    'UC_K9QJDV',  # 'ГРМ Бизнес',
                    'GOODS',  # 'ГРМ',
                    'UC_J426ZW',  # 'Садовод',
                    'UC_DBLSP5',  # 'Садовод+Помощник',
                    '9',  # 'БизнесСтарт',
                ],
                'CLOSED': 'N',  # Сделка не закрыта
                'CATEGORY_ID': '1',
            }
        }
                              )

    else: #если пятница, и на выходных не приходится конец месяца

        # Сделки ДК == с пятницы по воскресенье
        deals_dk = b.get_all('crm.deal.list', {
            'select': [
                'TITLE',
                'TYPE_ID',
                'STAGE_ID',
                'CLOSEDATE',
                'COMPANY_ID',
                'CLOSED',
                'CATEGORY_ID',
                'UF_CRM_1638958630625',
                'UF_CRM_1637933869479',
            ],
            'filter': {
                '>=CLOSEDATE': time_filter,
                '<=CLOSEDATE': date_end_filter_str,
                '!TYPE_ID': [
                    'UC_QQPYF0',  # Лицензия
                    'UC_OV4T7K',  # Отчетность (в рамках ИТС)
                    'UC_YIAJC8',  # Лицензия с купоном ИТС
                    'UC_74DPBQ',  # Битрикс24
                    # ИБС убираем КП и Фреши, согласно задаче 507278
                    'UC_HT9G9H',  # 'ПРОФ Земля',
                    'UC_XIYCTV',  # 'ПРОФ Земля+Помощник',
                    'UC_N113M9',  # 'ПРОФ Земля+Облако',
                    'UC_5T4MAW',  # 'ПРОФ Земля+Облако+Помощник',
                    'UC_ZKPT1B',  # 'ПРОФ Облако',
                    'UC_2SJOEJ',  # 'ПРОФ Облако+Помощник',
                    'UC_81T8ZR',  # 'АОВ',
                    'UC_SV60SP',  # 'АОВ+Облако',
                    'UC_92H9MN',  # 'Индивидуальный',
                    'UC_7V8HWF',  # 'Индивидуальный+Облако',
                    'UC_AVBW73',  # 'Базовый Земля',
                    'UC_GPT391',  # 'Базовый Облако',
                    'UC_1UPOTU',  # 'ИТС Бесплатный',
                    'UC_K9QJDV',  # 'ГРМ Бизнес',
                    'GOODS',  # 'ГРМ',
                    'UC_J426ZW',  # 'Садовод',
                    'UC_DBLSP5',  # 'Садовод+Помощник',
                    '9',  # 'БизнесСтарт',
                ],
                'CLOSED': 'N',  # Сделка не закрыта
                'CATEGORY_ID': '1',
            }
        }
                             )

        # Сделки ДПО == с пятницы по воскресенье
        deals_dpo = b.get_all('crm.deal.list', {
            'select': [
                'TITLE',
                'TYPE_ID',
                'STAGE_ID',
                'CLOSEDATE',
                'COMPANY_ID',
                'CLOSED',
                'CATEGORY_ID',
                'UF_CRM_1638958630625',
                'UF_CRM_1637933869479',
            ],
            'filter': {
                '>=UF_CRM_1638958630625': time_filter,
                '<=UF_CRM_1638958630625': date_end_filter_str,
                '!TYPE_ID': [
                    'UC_QQPYF0',  # Лицензия
                    'UC_OV4T7K',  # Отчетность (в рамках ИТС)
                    'UC_YIAJC8',  # Лицензия с купоном ИТС
                    'UC_74DPBQ',  # Битрикс24
                    # ИБС убираем КП и Фреши, согласно задаче 507278
                    'UC_HT9G9H',  # 'ПРОФ Земля',
                    'UC_XIYCTV',  # 'ПРОФ Земля+Помощник',
                    'UC_N113M9',  # 'ПРОФ Земля+Облако',
                    'UC_5T4MAW',  # 'ПРОФ Земля+Облако+Помощник',
                    'UC_ZKPT1B',  # 'ПРОФ Облако',
                    'UC_2SJOEJ',  # 'ПРОФ Облако+Помощник',
                    'UC_81T8ZR',  # 'АОВ',
                    'UC_SV60SP',  # 'АОВ+Облако',
                    'UC_92H9MN',  # 'Индивидуальный',
                    'UC_7V8HWF',  # 'Индивидуальный+Облако',
                    'UC_AVBW73',  # 'Базовый Земля',
                    'UC_GPT391',  # 'Базовый Облако',
                    'UC_1UPOTU',  # 'ИТС Бесплатный',
                    'UC_K9QJDV',  # 'ГРМ Бизнес',
                    'GOODS',  # 'ГРМ',
                    'UC_J426ZW',  # 'Садовод',
                    'UC_DBLSP5',  # 'Садовод+Помощник',
                    '9',  # 'БизнесСтарт',
                ],
                'CLOSED': 'N',  # Сделка не закрыта
                'CATEGORY_ID': '1',
            }
        }
                              )
        last_day_data = f'{current_year}-{current_month}-{last_day_current_month}'
        deals_dk = list(filter(lambda x: last_day_data not in x['CLOSEDATE'], deals_dk))
        deals_dpo = list(filter(lambda x: last_day_data not in x['UF_CRM_1638958630625'], deals_dpo))

    create_task(deals_dk, 'ДК')
    create_task(deals_dpo, 'ДПО')


if __name__ == '__main__':
    main()
