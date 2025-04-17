# -*- coding: utf-8 -*-
from Prolongation_ITS import prolongation_its
from SendNotification import send_notification


def main():

    try:
        prolongation_its()
    except:
        send_notification(['1','1391'], 'Работа прервана на создании задач "Пролонгация ИТС"')


main()