import re
from datetime import datetime, timedelta

import requests

from models import Feedback, Items
from service import send_message_to_group
from settings import BOT_TOKEN, GROUP_ID


class ParseWB:
    def __init__(self, sku: int):
        self.url = f"https://www.wildberries.ru/catalog/{sku}/detail.aspx"
        self.seller_id = self.__get_seller_id(self.url)

    @staticmethod
    def __get_item_id(url: str):
        """Получение id товара"""
        regex = "(?<=catalog/).+(?=/detail)"
        item_id = re.search(regex, url)[0]
        return item_id

    def __get_seller_id(self, url):
        """Получение id продавца"""
        response = requests.get(
            url=f"https://card.wb.ru/cards/detail?nm={self.__get_item_id(url=url)}"
        )
        seller_id = Items.model_validate(response.json()["data"])
        return seller_id.products[0].supplierId

    def parse(self):
        """Метод для парсинга основной информации"""
        _page = 1
        while True:
            response = requests.get(
                f"https://catalog.wb.ru/sellers/catalog?dest=-1257786&supplier={self.seller_id}&page={_page}",
            )
            _page += 1
            items_info = Items.model_validate(response.json()["data"])
            if not items_info.products:
                break
            self.__feedback(items_info)

    @staticmethod
    def __feedback(item_model: Items):
        """Получение feedbacks которые меньше 5 звёзд"""
        for product in item_model.products:
            url = f"https://feedbacks1.wb.ru/feedbacks/v1/{product.root}"
            res = requests.get(url=url)
            if res.status_code == 200 and res.json().get("feedbacks"):
                feedback = Feedback.model_validate(res.json())
                for x in feedback.feedbacks:
                    timestamp_string_without_microseconds = x.get("updatedDate").split(
                        "."
                    )[0]
                    try:
                        updated_date = datetime.strptime(
                            timestamp_string_without_microseconds, "%Y-%m-%dT%H:%M:%S"
                        )
                    except ValueError:
                        updated_date = datetime.strptime(
                            timestamp_string_without_microseconds, "%Y-%m-%dT%H:%M:%SZ"
                        )
                    current_time = datetime.utcnow()
                    time_difference = current_time - updated_date
                    if x.get("productValuation") < 5 and time_difference <= timedelta(
                        minutes=30
                    ):
                        review_type = "Негативный отзыв"
                        msg = (f"Тип отзыва: {review_type}\n"
                               f"Название товара: {product.name}\n"
                               f"SKU товара: {product.id}\n"
                               f"Отзыв: {x.get('productValuation')} звёзд\n"
                               f"Текст отзыва: {x.get('text')}\n"
                               f"Текущий рейтинг товара: {product.rating}")
                        send_message_to_group(BOT_TOKEN, GROUP_ID, msg)
