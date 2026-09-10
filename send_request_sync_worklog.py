import requests

from web_app_ip import web_app_ip


def send_request_sync_worklog():
    response = requests.get(
        url=f'{web_app_ip.rstrip("/")}/send_request_sync_worklog',
        timeout=(10, 1800),
        allow_redirects=False,
    )
    print(response.text)
    response.raise_for_status()
    if response.status_code != 200:
        raise RuntimeError(f'Неожиданный ответ HTTP {response.status_code}')


if __name__ == '__main__':
    send_request_sync_worklog()
