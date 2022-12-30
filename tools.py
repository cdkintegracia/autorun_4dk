import base64

import requests
from fast_bitrix24 import Bitrix

from authentication import authentication


b = Bitrix(authentication('Bitrix'))

def send_bitrix_request(method: str, data: dict):
    return requests.post(f"{authentication('Bitrix')}{method}", json=data).json()['result']

