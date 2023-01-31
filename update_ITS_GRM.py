# -*- coding: utf-8 -*-
from datetime import datetime

import ITS, GRM
from SendNotification import send_motification



def main():
    week_day = datetime.today().isoweekday()
    if week_day in [6, 7]:  # Выходные
        return
    ITS.main()
    print('ITS завершено')
    GRM.main()
    print('GRM завершено')
    send_motification(['311', '1'], 'Обновление ИТС и ГРМ завершено')

main()