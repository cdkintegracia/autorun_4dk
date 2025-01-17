# -*- coding: utf-8 -*-
from fast_bitrix24 import Bitrix
from authentication import authentication
from time import sleep

# Считывание файла authentication.txt

webhook = authentication('Bitrix')
b = Bitrix(webhook)


def main():

    activities = b.get_all('crm.activity.list', {'filter': {'PROVIDER_TYPE_ID': 'CALL', 'COMPLETED': 'N'}})

    if len(activities) != 0:
        for activity in activities:
            b.get_all('crm.activity.update', {'id': activity['ID'], 'fields': {'COMPLETED': 'Y'}})

    activities_email = b.get_all('crm.activity.list', {'filter': {'PROVIDER_TYPE_ID': 'EMAIL', 'COMPLETED': 'N'}})

    if len(activities_email) != 0:
        for activity in activities_email:
            b.get_all('crm.activity.update', {'id': activity['ID'], 'fields': {'COMPLETED': 'Y'}})

    activities_tasks_comments = b.get_all('crm.activity.list', {'filter': {'PROVIDER_TYPE_ID': 'TASKS_TASK_COMMENT', 'COMPLETED': 'N'}})
    if len(activities) != 0:
        for activity in activities:
            if count == 100:
                break
            try:
                b.get_all('crm.activity.update', {'id': activity['ID'], 'fields': {'COMPLETED': 'Y'}})
                print(count)
                sleep(2)
            except:
                sleep(2)

if __name__ == '__main__':
    main()
