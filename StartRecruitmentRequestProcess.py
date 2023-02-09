from datetime import datetime

from fast_bitrix24 import Bitrix

from authentication import authentication


b = Bitrix(authentication('Bitrix'))


def start_recruitment_request_process():
    if datetime.now().day != 25:
        return
    b.call('bizproc.workflow.start', {'TEMPLATE_ID': '1385', 'DOCUMENT_ID': ['lists', 'BizprocDocument', '371213']})


if __name__ == '__main__':
    start_recruitment_request_process()
