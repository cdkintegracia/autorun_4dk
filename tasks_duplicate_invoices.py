"""Напоминания о повторной отправке счетов за 7 календарных дней.

Запускать раз в будний день в окружении исходного tasks.py.
Используются прежние authentication('Bitrix') и fast_bitrix24.
В последний день месяца запуск разрешен, если это будний день.
В пятницу отбираются даты завершения через 7, 8 и 9 дней.
Даты завершения в конце месяца НЕ исключаются.
Повторный запуск может создать дубли, как и в исходном скрипте.
Дата и время берутся из локального времени сервера.
"""
from datetime import date, timedelta

EXCLUDED_TYPES = ['UC_QQPYF0', 'UC_OV4T7K', 'UC_YIAJC8', 'UC_74DPBQ', 'UC_HT9G9H', 'UC_XIYCTV', 'UC_N113M9', 'UC_5T4MAW', 'UC_ZKPT1B', 'UC_2SJOEJ', 'UC_81T8ZR', 'UC_SV60SP', 'UC_92H9MN', 'UC_7V8HWF', 'UC_AVBW73', 'UC_GPT391', 'UC_1UPOTU', 'UC_K9QJDV', 'GOODS', 'UC_J426ZW', 'UC_DBLSP5', '9']
AUTOPROLONGATION_FIELD = 'UF_CRM_1637933869479'


def closing_dates(today):
    """Даты завершения для сегодняшнего запуска."""
    if today.weekday() >= 5:
        return []
    return [today + timedelta(days=offset)
            for offset in (range(7, 10) if today.weekday() == 4 else [7])]


def create_sub_task(b, parent_id, deal, company_name, today):
    close_date = date.fromisoformat(deal['CLOSEDATE'][:10])
    days = (close_date - today).days
    links = [f"D_{deal['ID']}"]
    if deal.get('COMPANY_ID') and str(deal['COMPANY_ID']) != '0':
        links.append(f"CO_{deal['COMPANY_ID']}")
    b.call('tasks.task.add', {'fields': {
        'TITLE': f"Продублируйте счет {deal['TITLE']} клиенту",
        'DESCRIPTION': (
            f"Через {days} дней ({close_date:%d.%m.%Y}) завершается сделка "
            f"{deal['TITLE']} — {company_name}. "
            "Свяжитесь с менеджером или с клиентом и укажите в комментарии "
            "к задаче, что нужно сделать со сделкой."
        ),
        'DEADLINE': f'{today:%d.%m.%Y} 17:00',
        'RESPONSIBLE_ID': '173',
        'PARENT_ID': parent_id,
        'UF_CRM_TASK': links,
        'GROUP_ID': '77',
        'CREATED_BY': '173',
    }})


def create_check_list(b, rows, parent_id, title, today):
    if not rows:
        return
    checklist_id = b.call('task.checklistitem.add', {
        'taskId': int(parent_id), 'FIELDS': {'TITLE': title},
    }, raw=True)['result']
    for deal, company_name in rows:
        b.call('task.checklistitem.add', {
            'taskId': parent_id,
            'FIELDS': {
                'TITLE': (f"{deal['TITLE']} - {company_name} "
                          f"https://vc4dk.bitrix24.ru/crm/deal/details/{deal['ID']}/"),
                'PARENT_ID': checklist_id,
            },
        }, raw=True)
        create_sub_task(b, parent_id, deal, company_name, today)


def create_task(b, deals, today):
    if not deals:
        print('Подходящих сделок нет.')
        return
    groups = {False: [], True: []}
    companies = {}
    for deal in deals:
        company_id = str(deal.get('COMPANY_ID') or '0')
        if company_id not in companies:
            matches = (b.get_all('crm.company.list', {'filter': {'ID': company_id}})
                       if company_id != '0' else [])
            companies[company_id] = matches[0]['TITLE'] if matches else 'Компания не указана / недоступна'
        auto = str(deal.get(AUTOPROLONGATION_FIELD, '0')) != '0'
        groups[auto].append((deal, companies[company_id]))
    task = b.call('tasks.task.add', {'fields': {
        'TITLE': f'Продублируйте счета клиентам ({today:%d.%m.%Y})',
        'GROUP_ID': '11',
        'RESPONSIBLE_ID': '173',
        'CREATED_BY': '173',
    }}, raw=True)['result']['task']
    for auto, title in [(False, 'Сделки без автопролонгации'),
                        (True, 'Сделки с автопролонгацией')]:
        create_check_list(b, groups[auto], task['id'], title, today)
    print(f"Создана основная задача {task['id']}; подзадач: {len(deals)}")


def main():
    today = date.today()
    dates = closing_dates(today)
    if not dates:
        print('Выходной: задачи не создаются.')
        return
    from fast_bitrix24 import Bitrix
    from authentication import authentication
    b = Bitrix(authentication('Bitrix'))
    # Верхняя граница исключительная: включаем весь последний день,
    # даже если CLOSEDATE содержит время, отличное от полуночи.
    deals = b.get_all('crm.deal.list', {
        'select': ['ID', 'TITLE', 'CLOSEDATE', 'COMPANY_ID', AUTOPROLONGATION_FIELD],
        'filter': {
            '>=CLOSEDATE': dates[0].isoformat(),
            '<CLOSEDATE': (dates[-1] + timedelta(days=1)).isoformat(),
            '!TYPE_ID': EXCLUDED_TYPES,
            'CLOSED': 'N',
            'CATEGORY_ID': '1',
        },
    })
    create_task(b, deals, today)


if __name__ == '__main__':
    main()
