from pydantic import BaseModel


class Item(BaseModel):
    """Модель для продукта"""

    id: int
    name: str
    rating: int
    supplierId: int
    root: int


class Items(BaseModel):
    products: list[Item]


class Feedback(BaseModel):
    """Модель для feedback"""

    feedbacks: list
    feedbackCountWithText: int
    valuation: str
