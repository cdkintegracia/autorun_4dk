import requests

from web_app_ip import web_app_ip


def send_request_create_service_coverage_report():
    requests.get(url=f'{web_app_ip}/send_request_create_service_coverage_report')


if __name__ == '__main__':
    send_request_create_service_coverage_report()