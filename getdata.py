import sqlite3


def get_drinks():
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()

    query_gt = f"""
    SELECT Name, Ingredients, Price FROM MENU
    """
    cursor.execute(query_gt)

    drinks = cursor.fetchall()
    conn.commit()
    conn.close()

    return drinks


def get_desserts():
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()

    query_gt = f"""
    SELECT Name, Ingredients, Price FROM DESERTS
    """
    cursor.execute(query_gt)

    deserts = cursor.fetchall()
    conn.commit()
    conn.close()

    return deserts