from datetime import datetime

import requests


def update_service_sales_report():
    current_day = datetime.now().day
    '''
    if current_day != 1:
        return
    '''
    requests.get(url='http://141.8.195.67:5000/update_service_sales_report')


if __name__ == '__main__':
    update_service_sales_report()