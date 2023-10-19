from datetime import datetime

import requests
from web_app_ip import web_app_ip


def update_service_sales_report():
    return
    current_day = datetime.now().day
    if current_day != 1:
        return
    requests.get(url=f'{web_app_ip}/update_service_sales_report')


if __name__ == '__main__':
    update_service_sales_report()