# -*- coding: utf-8 -*-
import requests

import clear_calls, ITS, GRM, X_Report
from SendNotification import send_motification


def main():
    clear_calls.main()
    ITS.main()
    GRM.main()
    X_Report.main()
    requests.get(url='http://141.8.195.67:5000/')
    send_motification(['311', '1'], 'Автозапуск вечерних процессов завершен')


main()
