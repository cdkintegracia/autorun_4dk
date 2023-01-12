# -*- coding: utf-8 -*- 
import clear_calls, ITS, GRM, X_Report

from SendNotification import send_motification


def main():
    clear_calls.main()
    ITS.main()
    GRM.main()
    X_Report.main()
    send_motification(['311', '1'], 'Автозапуск вечерних процессов завершен')


main()
