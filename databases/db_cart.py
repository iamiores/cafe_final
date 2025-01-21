import sqlite3

def cart_table(users_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    query = f"""
    CREATE TABLE IF NOT EXISTS cart_{users_id} (
        name TEXT,
        ingredients TEXT,
        price TEXT
    );
    """
    cursor.execute(query)
    conn.commit()
    conn.close()

