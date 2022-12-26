import random
from sqlalchemy import select
from datetime import datetime, timedelta

from main import engine, stores, items, sales


conn = engine.connect()

for i in range(1, 21):
    ins = stores.insert().values(address='Street %d, %d' % (i, i*2))
    print(ins.compile().params)
    conn.execute(ins)

for i in range(1, 31):
    ins = items.insert().values(name='Item %d' % i, price=i*2.7)
    print(ins.compile().params)
    conn.execute(ins)

s_stores = select([stores])
rs = conn.execute(s_stores)
list_stores = [row.id for row in rs.fetchall()]
print(list_stores)

s_items = select([items])
rs = conn.execute(s_items)
list_items = [row.id for row in rs.fetchall()]
print(list_items)

for i in range(1, 51):
    id_stores = random.choice(list_stores)
    id_items = random.choice(list_items)
    ins = sales.insert().values(items_id=id_items, stores_id=id_stores, sale_time=datetime.now() - timedelta(days=i))
    print(ins.compile().params)
    conn.execute(ins)

conn.close()
