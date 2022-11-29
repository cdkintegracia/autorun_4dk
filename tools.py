import base64

import requests
from fast_bitrix24 import Bitrix

#from web_app_4dk.modules.authentication import authentication


def send_bitrix_request(method: str, data: dict):
    b = Bitrix('https://vc4dk.bitrix24.ru/rest/311/wkq0a0mvsvfmoseo/')
    return b.call(method, data)


