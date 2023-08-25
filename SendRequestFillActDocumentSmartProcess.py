import requests

from web_app_ip import web_app_ip


def send_request_fill_act_document_smart_process():
    requests.get(url=f'{web_app_ip}/send_request_fill_act_document_smart_process')


if __name__ == '__main__':
    send_request_fill_act_document_smart_process()