# -*- coding: utf-8 -*-
from datetime import datetime

import ITS, GRM
from SendNotification import send_notification



def main():
    week_day = datetime.today().isoweekday()
    if week_day in [1,2,3,4,5,6]:  # Выходные
        return
    try:
        GRM.main()
    except:
        send_notification(['1'], 'Не удалось обновить УС "ГРМ"')
    try:
        ITS.main()
    except:
        send_notification(['1'], 'Не удалось обновить УС "Отчет по сервисам"')
    send_notification(['1'], 'Обновление ИТС и ГРМ завершено')

main()
