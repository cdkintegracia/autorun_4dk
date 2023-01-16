# -*- coding: utf-8 -*-
import tasks, ClearListBP, X_Report
from Prolongation_ITS import prolongation_its



def main():
    prolongation_its()
    tasks.main()
    ClearListBP.clear_bp()
    X_Report.main()


main()