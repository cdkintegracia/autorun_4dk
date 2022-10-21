import time
from datetime import datetime
from datetime import timedelta

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


def create_check_list(data: dict, main_task_id: str, task_type: str):
    if not data:
        return

    main_checklist = b.call('task.checklistitem.add', [
        main_task_id, {
            # <Название компании> <Название сделки> <Ссылка на сделку>
            'TITLE': f"Сделки без автопролонгации", 'PARENT_ID': main_task_id,
        }
    ], raw=True
                            )

    for deal_id in data:
        b.call('task.checklistitem.add', [
            main_task_id, {
                'TITLE': f"{data[deal_id][0]} - {data[deal_id][1]} https://vc4dk.bitrix24.ru/crm/deal/details/{deal_id}/",
                'PARENT_ID': main_checklist['result'],
            }
        ], raw=True
               )

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
        }
               )

        create_check_list(no_autoprolongation_deals, task['task']['id'], task_type)
        create_check_list(autoprolongation_deals, task['task']['id'], task_type)


def main():
    week_day = datetime.today().isoweekday()
    if week_day in [6, 7]:  # Выходные
        return
    time_filter = time.strftime('%Y-%m-%d')     # Время для фильтра в битриксе
    date_end_filter = datetime.today() + timedelta(days=2)
    date_end_filter = date_end_filter.strftime('%Y-%m-%d')

    if week_day != 5:  # Пятница

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
                ],
                'CLOSED': 'N',  # Сделка не закрыта
                'CATEGORY_ID': '1',
            }
        }
                              )

    else:

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
                '<=CLOSEDATE': date_end_filter,
                '!TYPE_ID': [
                    'UC_QQPYF0',  # Лицензия
                    'UC_OV4T7K',  # Отчетность (в рамках ИТС)
                    'UC_YIAJC8',  # Лицензия с купоном ИТС
                    'UC_74DPBQ',  # Битрикс24
                ],
                'CLOSED': 'N',  # Сделка не закрыта
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
                '<=UF_CRM_1638958630625': date_end_filter,
                '!TYPE_ID': [
                    'UC_QQPYF0',  # Лицензия
                    'UC_OV4T7K',  # Отчетность (в рамках ИТС)
                    'UC_YIAJC8',  # Лицензия с купоном ИТС
                    'UC_74DPBQ',  # Битрикс24
                ],
                'CLOSED': 'N',  # Сделка не закрыта
            }
        }
                              )


    create_task(deals_dk, 'ДК')
    create_task(deals_dpo, 'ДПО')


if __name__ == '__main__':
    main()
