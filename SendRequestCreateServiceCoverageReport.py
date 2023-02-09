from fast_bitrix24 import Bitrix
import requests

from authentication import authentication

b = Bitrix(authentication('Bitrix'))


def send_request_create_service_coverage_report():
    requests.get(url='http://141.8.195.67:5000/send_request_create_service_coverage_report')


if __name__ == '__main__':
    send_request_create_service_coverage_report()