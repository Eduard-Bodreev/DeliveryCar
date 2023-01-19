import sqlite3 as sq
import re


async def db_start():
    global db, cur

    db = sq.connect('new.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS customer(customer_id TEXT PRIMARY KEY, user_id INTEGER, role TEXT, "
                "adr_to TEXT, timing TEXT, radius TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS deliver(deliver_id TEXT PRIMARY KEY, user_id INTEGER, role TEXT, adr TEXT, "
                "latitude REAL, longitude REAL, car_app TEXT, car_mark TEXT,  remoteness TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS orders(user_id TEXT PRIMARY KEY, customer_id INTEGER , deliver_id INTEGER, "
                "status TEXT)")

    db.commit()


async def create_customer(customer_id):
    user = cur.execute("SELECT 1 FROM customer WHERE customer_id == '{key}'".format(key=customer_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO customer VALUES(?, ?, ?, ?, ?, ?)",
                    (customer_id, '', '', '', '', ''))
        db.commit()


async def create_deliver(deliver_id):
    user = cur.execute("SELECT 1 FROM deliver WHERE deliver_id == '{key}'".format(key=deliver_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO deliver VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (deliver_id, '', '', '', '', '', '', '', ''))
        db.commit()


async def create_orders(user_id):
    user = cur.execute("SELECT 1 FROM orders WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO orders VALUES(?, ?, ?, ?)",
                    (user_id, '', '', ''))
        db.commit()


async def edit_customer(state, customer_id, user_id):
    async with state.proxy() as data:
        cur.execute("UPDATE customer SET user_id = '{}', role= '{}', adr_to= '{}', timing= '{}', radius= '{}' WHERE "
                    "customer_id == '{}'".format(user_id, data['role'], data['adr_to'], data['timing'], data['radius'],
                                                 customer_id))
        db.commit()


async def edit_deliver(state, deliver_id, user_id):
    async with state.proxy() as data:
        cur.execute(
            "UPDATE deliver SET user_id='{}', role= '{}', adr= '{}', latitude= '{}', longitude= '{}', car_app= '{}', "
            "car_mark= '{}', remoteness= '{}' WHERE deliver_id == '{}'".format(user_id, data['role'],
                                                                               data['adr'], data['latitude'],
                                                                               data['longitude'], data['car_app'],
                                                                               data['car_mark'], data['remoteness'],
                                                                               deliver_id))
        db.commit()


async def edit_orders(state, user_id):
    async with state.proxy() as data:
        cur.execute("UPDATE orders SET customer_id= '{}', deliver_id= '{}', status= '{}' WHERE user_id == '{}'".format(
            data['customer_id'], data['deliver_id'], data['status'], user_id))
        db.commit()


async def upd_orders(status, column, user_id):
    cur.execute("UPDATE orders SET c status= '{}' WHERE {} == '{}'".format(status, column, user_id))
    db.commit()


async def add_customer(state, customer_id, user_id):
    user = cur.execute("SELECT 1 FROM customer WHERE customer_id == '{key}'".format(key=customer_id)).fetchone()
    if not user:
        async with state.proxy() as data:
            cur.execute("INSERT INTO customer VALUES(?, ?, ?, ?, ?, ?)",
                        (customer_id, user_id, data['role'], data['adr_to'], data['timing'], data['radius']))
    db.commit()


async def add_deliver(state, deliver_id, user_id):
    user = cur.execute("SELECT 1 FROM orders WHERE deliver_id == '{key}'".format(key=deliver_id)).fetchone()
    if not user:
        async with state.proxy() as data:
            cur.execute("INSERT INTO deliver VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (deliver_id, user_id, data['role'], data['adr'], data['latitude'], data['longitude'],
                         data['car_app'], data['car_mark'], data['remoteness']))

    db.commit()


async def add_orders(state, user_id):
    user = cur.execute("SELECT 1 FROM orders WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        async with state.proxy() as data:
            cur.execute("INSERT INTO orders VALUES(?, ?, ?, ?)",
                        (user_id, data['customer_id'], data['deliver_id'], data['status']))
    db.commit()


async def remove_deliver(deliver_id):
    return cur.execute("DELETE FROM deliver WHERE deliver_id == '{key}'".format(key=deliver_id))


async def remove_customer(customer_id):
    return cur.execute("DELETE FROM customer WHERE customer_id == '{key}'".format(key=customer_id))


async def send_customer():
    query = 'SELECT * FROM customer'
    cur.execute(query)
    data = cur.fetchall()
    mm = []
    for i in data:
        mm.append(i)
    ww = len(data)
    g = []
    for i in range(ww):
        a = re.sub('|\(|\'|\)', '', str(mm[i]))
        g.append(a)
    c = []
    for i in g:
        q = i + "; \n"
        c.append(q)
    val = '\n'.join(c)
    return val


async def send_deliver():
    query = 'SELECT * FROM deliver'
    cur.execute(query)
    data = cur.fetchall()
    mm = []
    for i in data:
        mm.append(i)
    ww = len(data)
    g = []
    for i in range(ww):
        a = re.sub('|\(|\'|\)', '', str(mm[i]))
        g.append(a)
    c = []
    for i in g:
        q = i + "; \n"
        c.append(q)
    val = '\n'.join(c)
    return val


async def send_orders():
    query = 'SELECT * FROM orders'
    cur.execute(query)
    data = cur.fetchall()
    mm = []
    for i in data:
        mm.append(i)
    ww = len(data)
    g = []
    for i in range(ww):
        a = re.sub('|\(|\'|\)', '', str(mm[i]))
        g.append(a)
    c = []
    for i in g:
        q = i + "; \n"
        c.append(q)
    val = '\n'.join(c)
    return val


async def get_cus(user_id):
    result = cur.execute("SELECT timing FROM customer WHERE user_id = '{}'".format(user_id))
    db.commit()
    return result.fetchone()


async def get_del_id(zalupa):
    del_id = "SELECT deliver_id FROM orders WHERE customer_id = '{}' AND status = 'создан'".format(zalupa)
    cur.execute(del_id)
    data = cur.fetchone()
    mm = []
    for i in data:
        mm.append(i)
    ww = len(data)
    g = []
    for i in range(ww):
        a = re.sub('|\(|\'|\,|\)', '', str(mm[i]))
        g.append(a)
    c = []
    for i in g:
        c.append(i)
    val = ''.join(c)
    return val


async def get_cus_id(zalupa):
    cus_id = "SELECT customer_id FROM orders WHERE deliver_id = '{}' AND status = 'создан'".format(zalupa)
    cur.execute(cus_id)
    data = cur.fetchone()
    mm = []
    for i in data:
        mm.append(i)
    ww = len(data)
    g = []
    for i in range(ww):
        a = re.sub('|\(|\'|\,|\)', '', str(mm[i]))
        g.append(a)
    c = []
    for i in g:
        c.append(i)
    val = ''.join(c)
    return val


async def get_cus_idd(zalupa):
    cus_id = cur.execute("SELECT customer_id FROM orders WHERE deliver_id = '{}' AND status = 'создан'".format(zalupa))
    return cus_id.fetchone()


async def get_latitude(zalupa):
    adr = "SELECT latitude FROM deliver LEFT JOIN orders ON deliver.user_id= orders.deliver_id WHERE customer_id = " \
          "'{}' ".format(zalupa)
    cur.execute(adr)
    data = cur.fetchone()
    mm = []
    for i in data:
        mm.append(i)
    ww = len(data)
    g = []
    for i in range(ww):
        a = re.sub('|\(|\'|\,|\)', '', str(mm[i]))
        g.append(a)
    c = []
    for i in g:
        c.append(i)
    val = ''.join(c)
    return val


async def get_longitude(zalupa):
    adr = "SELECT longitude FROM deliver LEFT JOIN orders ON deliver.user_id= orders.deliver_id WHERE customer_id = " \
          "'{}' AND status = 'создан' ".format(zalupa)
    cur.execute(adr)
    data = cur.fetchone()
    mm = []
    for i in data:
        mm.append(i)
    ww = len(data)
    g = []
    for i in range(ww):
        a = re.sub('|\(|\'|\,|\)', '', str(mm[i]))
        g.append(a)
    c = []
    for i in g:
        c.append(i)
    val = ''.join(c)
    return val


async def select(column, table, marker, zalupa):
    cus_id = cur.execute("SELECT {} FROM {} WHERE {} = '{}'".format(column, table, marker, zalupa))
    db.commit()
    return cus_id.fetchone()
