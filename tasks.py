from fast_bitrix24 import Bitrix
import time
from authentication import authentication


# Считывание файла authentication.txt

webhook = authentication('Bitrix')
b = Bitrix(webhook)


def create_task(deals, task_type):

    task_types = {
        'ДК': 'Эти сделки завершаются сегодня',
        'ДПО': 'Внимание! Наступила дата проверки оплаты для сделок'
    }

    autoprolongation_deals = []
    no_autoprolongation_deals = []

    for deal in deals:

        # Получение названия компании

        company = b.get_all('crm.company.list', {'filter': {'ID': deal['COMPANY_ID']}})[0]

        # Формирование текста для задачи
        if deal['UF_CRM_1637933869479'] == '0':
            no_autoprolongation_deals.append(f""
                         f"{deal['TITLE']} - "
                         f"{company['TITLE']} "
                         f"https://vc4dk.bitrix24.ru/crm/deal/details/{deal['ID']}/\n")
        else:
            autoprolongation_deals.append(f""
                         f"{deal['TITLE']} - "
                         f"{company['TITLE']} "
                         f"https://vc4dk.bitrix24.ru/crm/deal/details/{deal['ID']}/\n")

    # Создание задачи

    time_task = time.strftime('%d.%m.%Y')  # Время для названия задачи

    if autoprolongation_deals or no_autoprolongation_deals:

        task = b.call('tasks.task.add', {'fields': {
            'TITLE': f'{task_types[task_type]} ({time_task})',
            'GROUP_ID': '11',
            'RESPONSIBLE_ID': '311',
            'CREATED_BY': '173'
        }
        }
               )

        main_checklist = b.call('task.checklistitem.add', [
            task['task']['id'], {
                # <Название компании> <Название сделки> <Ссылка на сделку>
                'TITLE': f"Сделки с автопролонгацией", 'PARENT_ID': task['task']['id'],
            }
        ], raw=True
               )

        for text in autoprolongation_deals:
            b.call('task.checklistitem.add', [
                task['task']['id'], {
                    'TITLE': text, 'PARENT_ID': main_checklist['result'],
                }
            ], raw=True
                   )

        main_checklist = b.call('task.checklistitem.add', [
            task['task']['id'], {
                # <Название компании> <Название сделки> <Ссылка на сделку>
                'TITLE': f"Сделки без автопролонгации", 'PARENT_ID': task['task']['id'],
            }
        ], raw=True
                                )

        for text in no_autoprolongation_deals:
            b.call('task.checklistitem.add', [
                task['task']['id'], {
                    'TITLE': text, 'PARENT_ID': main_checklist['result'],
                }
            ], raw=True
                   )




def main():

    time_filter = time.strftime('%Y-%m-%d')     # Время для фильтра в битриксе

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
    }
    }
                  )

    create_task(deals_dk, 'ДК')

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
        'UF_CRM_1638958630625': time_filter,   # ДПО == текущая дата
        '!TYPE_ID': [
            'UC_QQPYF0',    # Лицензия
            'UC_OV4T7K',    # Отчетность (в рамках ИТС)
            'UC_YIAJC8',    # Лицензия с купоном ИТС
            'UC_74DPBQ',     # Битрикс24
        ],
        'CLOSED': 'N',  # Сделка не закрыта
    }
    }
                  )

    create_task(deals_dpo, 'ДПО')


if __name__ == '__main__':
    main()
