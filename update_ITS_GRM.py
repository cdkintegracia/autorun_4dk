# -*- coding: utf-8 -*-
import ITS, GRM
from SendNotification import send_motification


def main():
    ITS.main()
    print('ITS завершено')
    GRM.main()
    print('GRM завершено')
    send_motification(['311', '1'], 'Обновление ИТС и ГРМ завершено')

main()