from typing import List
from fastapi import FastAPI
import databases
import sqlalchemy
from sqlalchemy.sql import func
from datetime import datetime
from dateutil.relativedelta import *

from models import Item, Store, SalesIn, SalesOut, StoreTop, ItemTop


DATABASE_URL = "sqlite:///./stores.db"
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

stores = sqlalchemy.Table(
    "stores",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("address", sqlalchemy.String),
)

items = sqlalchemy.Table(
    "items",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, unique=True),
    sqlalchemy.Column("price", sqlalchemy.Float),
)

sales = sqlalchemy.Table(
    "sales",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("sale_time", sqlalchemy.DateTime, default=datetime.now),
    sqlalchemy.Column('items_id', sqlalchemy.Integer, sqlalchemy.ForeignKey("items.id")),
    sqlalchemy.Column('stores_id', sqlalchemy.Integer, sqlalchemy.ForeignKey("stores.id")),
)


engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/items/", response_model=List[Item])
async def read_items():
    # query = items.select()
    query = sqlalchemy.select(items)
    return await database.fetch_all(query)


@app.get("/stores/", response_model=List[Store])
async def read_stores():
    query = stores.select()
    return await database.fetch_all(query)


@app.post("/sales/", response_model=SalesOut)
async def create_sale(sale: SalesIn):
    query = sales.insert().values(items_id=sale.items_id, stores_id=sale.stores_id, sale_time=datetime.now())
    # print(query.compile().params)
    last_record_id = await database.execute(query)

    query = sales.select().filter(sales.c.id == last_record_id).limit(1)
    return await database.fetch_one(query)


@app.get("/stores/top/", response_model=List[StoreTop])
async def read_stores_top():
    date_start = datetime.now() + relativedelta(months=-1)

    query = sqlalchemy.select([stores.c.id, stores.c.address, func.sum(items.c.price).label('income')]). \
        select_from(sales.join(stores).join(items)). \
        where(sales.c.sale_time > date_start). \
        group_by(sales.c.stores_id). \
        order_by(sqlalchemy.desc("income")). \
        limit(10)

    return await database.fetch_all(query)


@app.get("/items/top/", response_model=List[ItemTop])
async def read_items_top():
    query = sqlalchemy.select([items.c.id, items.c.name, func.count("*").label('sales_amount')]). \
        select_from(sales.join(items)). \
        group_by(sales.c.items_id). \
        order_by(sqlalchemy.desc("sales_amount")). \
        limit(10)

    return await database.fetch_all(query)
