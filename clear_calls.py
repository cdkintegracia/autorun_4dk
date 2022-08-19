# -*- coding: utf-8 -*-
from fast_bitrix24 import Bitrix


def main():
    # Считывание файла authentication.txt

    with open('authentication.txt') as file:
        lines = file.readlines()
        authentication = {}
        for line in lines:
            lst = line.split(': ')
            authentication.setdefault(lst[0], lst[1].strip())

    # Вебхук для доступа к Bitrix24
    webhook = authentication['Bitrix']
    b = Bitrix(webhook)

    activities = b.get_all('crm.activity.list', {'filter': {'PROVIDER_TYPE_ID': 'CALL', 'COMPLETED': 'N'}})

    if len(activities) != 0:
        for activity in activities:
            b.get_all('crm.activity.update', {'id': activity['ID'], 'fields': {'COMPLETED': 'Y'}})


if __name__ == '__main__':
    main()
