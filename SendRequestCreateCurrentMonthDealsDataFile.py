from calendar import monthrange
from datetime import datetime

import requests

from SendNotification import send_notification


def send_request_create_current_month_deals_data_file():
    month_days_range = monthrange(datetime.now().year, datetime.now().month)[1]
    if datetime.now().day != month_days_range:
        return
    requests.get(url='http://141.8.195.67:5000/create_current_month_deals_data_file')
    send_notification(['311', '1'], 'Создан файл с информацией по сделкам для отчета по сумме сервисов')


if __name__ == '__main__':
    send_request_create_current_month_deals_data_file()
