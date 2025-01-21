import sqlite3

table_name = "users"

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

query_cr_tb = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        PhoneNum TEXTUNIQUE,
        Age TEXT,
        Password TEXT
    );
"""
cursor.execute(query_cr_tb)
conn.commit()
conn.close()