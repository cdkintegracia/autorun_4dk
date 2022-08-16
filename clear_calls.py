# -*- coding: utf-8 -*-
from fast_bitrix24 import Bitrix


def main():

    webhook = 'https://vc4dk.bitrix24.ru/rest/311/r1oftpfibric5qym/'
    b = Bitrix(webhook)
    activities = b.get_all('crm.activity.list', {'filter': {'PROVIDER_TYPE_ID': 'CALL', 'COMPLETED': 'N'}})

    if len(activities) != 0:
        for activity in activities:
            b.get_all('crm.activity.update', {'id': activity['ID'], 'fields': {'COMPLETED': 'Y'}})


if __name__ == '__main__':
    main()
