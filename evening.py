# -*- coding: utf-8 -*-
import clear_calls, X_Report
from SendNotification import send_motification
from SendRequestCreateCurrentMonthDealsDataFile import send_request_create_current_month_deals_data_file
from UpdateDailyTaskStatistic import update_daily_task_statistic


def main():
    clear_calls.main()
    print('clear_calls завершено')
    update_daily_task_statistic()
    print('update_daily_task_statistic завершено')
    send_request_create_current_month_deals_data_file()
    print('send_request_create_current_month_deals_data_file завершено')
    X_Report.main()
    print('X-report завершено')
    send_motification(['311', '1'], 'Автозапуск вечерних процессов завершен')


main()
