# -*- coding: utf-8 -*-
import clear_calls, X_Report
from SendNotification import send_notification
from SendRequestCreateCurrentMonthDealsDataFile import send_request_create_current_month_deals_data_file
from UpdateDailyTaskStatistic import update_daily_task_statistic
from DeleteDismissedUserVacation import delete_dismissed_user_vacation

def main():
    try:
        clear_calls.main()
    except:
        send_notification(['1'], 'Работа вечерних процессов прервана на завершении дел со звонками')
    try:
        update_daily_task_statistic()
    except:
        send_notification(['1'], 'Работа вечерних процессов прервана на обновлении отчета по задачам')
    try:
        send_request_create_current_month_deals_data_file()
    except:
        send_notification(['1'], 'Работа вечерних процессов прервана на выгрузке сделок для отчета')
    '''
    try:
        X_Report.main()
    except:
        send_notification(['1'], 'Работа вечерних процессов прервана на обновлении X-отчета')
    '''
    delete_dismissed_user_vacation()
    send_notification(['1'], 'Автозапуск вечерних процессов завершен')


main()
