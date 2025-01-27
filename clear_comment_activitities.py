# -*- coding: utf-8 -*-
from fast_bitrix24 import Bitrix
from authentication import authentication
from time import sleep

# Считывание файла authentication.txt

webhook = authentication('Bitrix')
b = Bitrix(webhook)


def main():
    count = 0
    activities_tasks_comments = b.get_all('crm.activity.list', {'filter': {'PROVIDER_TYPE_ID': 'TASKS_TASK_COMMENT', 'COMPLETED': 'N'}})
    if len(activities_tasks_comments) != 0:
        for activity in activities_tasks_comments:
            if count == 100:
                break
            try:
                b.get_all('crm.activity.update', {'id': activity['ID'], 'fields': {'COMPLETED': 'Y'}})
                print(count)
                sleep(2)
                count+=1
            except:
                sleep(2)

if __name__ == '__main__':
    main()
