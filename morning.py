# -*- coding: utf-8 -*-
import tasks, ClearListBP, X_Report
from Prolongation_ITS import prolongation_its
from SendCompanyInteractionInfo import send_company_interaction_info
from UpdateServiceSalesReport import update_service_sales_report
from StartRecruitmentRequestProcess import start_recruitment_request_process



def main():
    prolongation_its()
    tasks.main()
    send_company_interaction_info()
    ClearListBP.clear_bp()
    update_service_sales_report()
    start_recruitment_request_process()
    X_Report.main()


main()