from fast_bitrix24 import Bitrix
import requests

from authentication import authentication
from web_app_ip import web_app_ip

b = Bitrix(authentication('Bitrix'))


def send_request_create_service_coverage_report():
    requests.get(url=f'{web_app_ip}/send_request_create_service_coverage_report')


if __name__ == '__main__':
    send_request_create_service_coverage_report()