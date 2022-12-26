from pydantic import BaseModel
from datetime import datetime


class Item(BaseModel):
    id: int
    name: str
    price: float


class Store(BaseModel):
    id: int
    address: str


class SalesIn(BaseModel):
    items_id: int
    stores_id: int


class SalesOut(BaseModel):
    id: int
    sale_time: datetime
    items_id: int
    stores_id: int


class StoreTop(BaseModel):
    id: int
    address: str
    income: float


class ItemTop(BaseModel):
    id: int
    name: str
    sales_amount: int
