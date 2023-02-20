# -*- coding: utf-8 -*-
from CheckDealStage import check_deal_stage
from UpdateDeal1cCode import update_deal_1c_code
from CreateCallStatisticNullElements import create_call_statistic_null_elements
from UpdateUserActivityStatistic import update_user_activity_statistic
from SendNotification import send_notification


def main():
    try:
        check_deal_stage()
    except:
        send_notification(['1', '311'], 'Работа ночных процессов прервана на актуализации стадий сделок')
    try:
        update_deal_1c_code()
    except:
        send_notification(['1', '311'], 'Работа ночных процессов прервана на обновлении "СлужКод1с"')
    try:
        create_call_statistic_null_elements()
    except:
        send_notification(['1', '311'], 'Работа ночных процессов прервана на создании нулевых элементов УС "Статистика звонков"')
    try:
        update_user_activity_statistic()
    except:
        send_notification(['1', '311'], 'Работа ночных процессов прервана на обновлении отчета по активности пользователей')


main()