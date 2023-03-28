# -*- coding: utf-8 -*-
import CheckMailStatus
from SendNotification import send_notification


def main():
    CheckMailStatus.main()
    '''
    try:
        CheckMailStatus.main()
    except:
        send_notification(['1', '311'], 'Процесс по проверке статуса отправленных писем не был завершен')
    '''


main()