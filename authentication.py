import base64


def authentication(key):
    credentials = {
        'Bitrix': 'aHR0cHM6Ly92YzRkay5iaXRyaXgyNC5ydS9yZXN0LzEvaG51dG8yanZvazY2cHVwbS8=',
        'Google': 'Yml0cml4MjQtZGF0YS1zdHVkaW8tMjI3OGM3YmZiMWE3Lmpzb24=',
        '1c@gk4dk.ru': 'Q1JZMWJtOEhqQlRoaHMwSmU1R20=',
        #'Yandex': 'eTBfQWdBQUFBQVlBQkR1QUFvdmJRQUFBQURueE43OFZHcTlncnEwUWJHcUJPT3RvZW1palNmWjBRMA==',
        'Yandex': 'eTBfQWdBQUFBQnhaYUdFQUFxbW93QUFBQUR2QkdGS0V0amRTaTkwVDR5RW03SmUyRkVQMlhqYnU0dw==',
        'Chat-bot': 'aHR0cHM6Ly92YzRkay5iaXRyaXgyNC5ydS9yZXN0LzEvYWZzYmttMzB3MWlwN2Mxei8K',
    }
    return base64.b64decode(credentials[key]).decode('utf-8')
