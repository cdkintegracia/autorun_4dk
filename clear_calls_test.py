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
    activities = b.get_all('crm.activity.list', {'filter': {'PROVIDER_TYPE_ID': 'TASKS_TASK_COMMENT', 'COMPLETED': 'N'}})
    print(len(activities))
    if len(activities) != 0:
        count = 0
        for activity in activities:
            if count == 200:
                break
            try:
                b.get_all('crm.activity.update', {'id': activity['ID'], 'fields': {'COMPLETED': 'Y'}})
                print(activity['ID'])
                print(count)
                count+=1
                sleep(2)
            except:
                print("oops")
                sleep(2)


if __name__ == '__main__':
    main()
