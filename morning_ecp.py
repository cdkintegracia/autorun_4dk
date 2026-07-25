# -*- coding: utf-8 -*-
import tasks, ClearListBP, X_Report
from Prolongation_ITS import prolongation_its
from UpdateServiceSalesReport import update_service_sales_report
from StartRecruitmentRequestProcess import start_recruitment_request_process
from SendNotification import send_notification
from CreateCallRedirectionTasks import create_call_redirection_tasks
from SendDealEndingMessageBot import send_deal_ending_message_bot
from SendingEmailsPlan import sending_emails_plan
from EcpDealEnding import ecp_deal_ending
from SendRequestFillActDocumentSmartProcess import send_request_fill_act_document_smart_process


def main():

    try:
        ecp_deal_ending()
    except:
        send_notification(['1','1391'], 'Работа утренних процессов прервана на создании задачи об окончании ЭЦП')
    


main()