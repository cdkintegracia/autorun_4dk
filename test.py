# -*- coding: utf-8 -*-
from fast_bitrix24 import Bitrix
from authentication import authentication
from time import sleep
# Считывание файла authentication.txt

webhook = authentication('Bitrix')
b = Bitrix(webhook)


def main():

    '''
    b.get_all('crm.activity.update', {'id': 1053653, 'fields': {'COMPLETED': 'Y'}})
    '''
    ridss = b.get_all('user.get', {
        'filter': {
            'UF_DEPARTMENT': ['225'] #обновлен айди отдела
        }
    })
    print(ridss)


if __name__ == '__main__':
    main()
