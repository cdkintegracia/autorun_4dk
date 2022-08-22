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
    task_text = ''  # Текст для задачи

    for number, deal in enumerate(deals, start=1):

        # Получение названия компании

        company = b.get_all('crm.company.list', {'filter': {'ID': deal['COMPANY_ID']}})[0]

        # Формирование текста для задачи

        task_text += f"{number}. " \
                     f"{deal['TITLE']} - " \
                     f"{company['TITLE']} " \
                     f"https://vc4dk.bitrix24.ru/crm/deal/details/{deal['ID']}/\n"

    # Создание задачи

    if task_text != '':

        b.call('tasks.task.add', {'fields': {
            'TITLE': f'{task_types[task_type]} ({time_task})',
            'GROUP_ID': '13',
            'DESCRIPTION': task_text,
            'RESPONSIBLE_ID': '311'
        }
        }
               )

time_filter = time.strftime('%Y-%m-%d')     # Время для фильтра в битриксе
time_task = time.strftime('%d.%m.%Y')   # Время для названия задачи

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
        'UF_CRM_1638958630625'
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
        'UF_CRM_1638958630625'
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
