from calendar import monthrange
from datetime import datetime

import requests

from SendNotification import send_motification


def send_request_create_current_month_deals_data_file():
    month_days_range = monthrange(datetime.now().year, datetime.now().month)[1]
    if datetime.now().day != month_days_range:
        send_motification(['311'], 'Не конец месяца для создания месячного файла со сделками')
        return
    requests.get(url='http://141.8.195.67:5000/create_current_month_deals_data_file')
    send_motification(['311', '1'], 'Создан файл с информацией по сделкам для отчета по сумме сервисов')
