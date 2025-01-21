import sqlite3

def orders_table(users_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    query = f"""
    CREATE TABLE IF NOT EXISTS orders_{users_id} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price TEXT,
        phonenum TEXT,
        time INTEGER,
        time_created INTEGER
    );
    """
    cursor.execute(query)
    conn.commit()
    conn.close()

# conn = sqlite3.connect('users.db')
# cursor = conn.cursor()

# query = """
#     DROP TABLE orders_1;
# """
# cursor.execute(query)
# conn.commit()
# conn.close()