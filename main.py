from parser import ParseWB

import schedule

from service import read_sku_from_excel
from settings import file_path


def digest_task():
    sku_list = read_sku_from_excel(file_path)
    for sku in sku_list:
        ParseWB(sku).parse()


if __name__ == "__main__":
    digest_task()
    schedule.every(30).minutes.do(digest_task)
    while True:
        schedule.run_pending()
