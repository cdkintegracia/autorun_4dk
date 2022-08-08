# -*- coding: utf-8 -*-
import schedule
import clear_calls
import ITS


def main():
    clear_calls.main()
    ITS.main()


schedule.every().day.at("18:00").do(main)

while True:
    schedule.run_pending()
