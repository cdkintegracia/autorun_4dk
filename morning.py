# -*- coding: utf-8 -*-
import tasks, ClearListBP, X_Report
from Prolongation_ITS import prolongation_its
from SendCompanyInteractionInfo import send_company_interaction_info
from UpdateServiceSalesReport import update_service_sales_report
from StartRecruitmentRequestProcess import start_recruitment_request_process
from SendNotification import send_notification
from CreateCallRedirectionTasks import create_call_redirection_tasks
from SendDealEndingMessageBot import send_deal_ending_message_bot
from SendingEmailsPlan import sending_emails_plan
from EcpDealEnding import ecp_deal_ending
from SendRequestFillActDocumentSmartProcess import send_request_fill_act_document_smart_process


def main():
    send_request_fill_act_document_smart_process()
    try:
        sending_emails_plan()
        send_deal_ending_message_bot()
    except:
        send_notification(['1', '311'], 'Работа утренних процессов прервана на отправке сообщений об окончании сделок')
    try:
        prolongation_its()
    except:
        send_notification(['1', '311'], 'Работа утренних процессов прервана на создании задач "Пролонгация ИТС"')
    try:
        tasks.main()
    except:
        send_notification(['1', '311'], 'Работа утренних процессов прервана на создании задач о завершающихся сделках')
    try:
        send_company_interaction_info()
    except:
        send_notification(['1', '311'], 'Работа утренних процессов прервана на отправке отчетов о взаимодействии с компаниями')
    try:
        update_service_sales_report()
    except:
        send_notification(['1', '311'], 'Работа утренних процессов прервана на обновлении отчета по сумме сервисов')
    try:
        ecp_deal_ending()
    except:
        send_notification(['1', '311'], 'Работа утренних процессов прервана на создании задачи об окончании ЭЦП')
    create_call_redirection_tasks()
    '''
    try:
        start_recruitment_request_process()
    except:
        send_notification(['1', '311'], 'Работа утренних процессов прервана на создании заданий на запрос персонала')
    try:
        X_Report.main()
    except:
        send_notification(['1', '311'], 'Работа утренних процессов прервана на обновлении X-отчета')
    '''


main()