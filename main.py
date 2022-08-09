# -*- coding: utf-8 -*-
import schedule
import clear_calls
import ITS
import GRM


def main():
    clear_calls.main()
    ITS.main()
    GRM.main()


schedule.every().day.at("18:00").do(main)

while True:
    schedule.run_pending()
