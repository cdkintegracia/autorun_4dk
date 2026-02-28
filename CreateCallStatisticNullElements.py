from datetime import datetime
from time import sleep

from fast_bitrix24 import Bitrix

from ElementCallStatistic import create_element
from authentication import authentication


b = Bitrix(authentication('Bitrix'))


def create_call_statistic_null_elements():
    current_date = datetime.now()

    if current_date.day != 1:
        return

    companies = b.get_all('crm.company.list')
    count = 0
    for company in companies:
        create_element(company['ID'], responsible=company['ASSIGNED_BY_ID'])
        count += 1
        sleep(1)
        print(f'{count} | {len(companies)}')


if __name__ == '__main__':
    create_call_statistic_null_elements()