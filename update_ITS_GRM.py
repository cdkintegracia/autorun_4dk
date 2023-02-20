# -*- coding: utf-8 -*-
from datetime import datetime

import ITS, GRM
from SendNotification import send_notification



def main():
    week_day = datetime.today().isoweekday()
    if week_day in [6, 7]:  # Выходные
        return
    try:
        GRM.main()
    except:
        send_notification(['1', '311'], 'Не удалось обновить УС "ГРМ" и УС "Отчет по сервисам"')
    try:
        ITS.main()
    except:
        send_notification(['1', '311'], 'Не удалось обновить УС "Отчет по сервисам"')
    send_notification(['311', '1'], 'Обновление ИТС и ГРМ завершено')

main()