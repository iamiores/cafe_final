import sqlite3
import sys

# налаштування показу тексту в юнікоді utf-8, щоб текст показувався без проблем
sys.stdout.reconfigure(encoding="utf-8")


table_name = "MENU"


def add_stuff():
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()

    try:
        while True:
            name = str(input("Введіть назву напою/десерту: ")).strip()
            if name:
                break
            print("Поле не може бути порожнім. Спробуйте ще раз.")

        while True:
            ingredients = str(input("Введіть інгредієнти: ")).strip()
            if ingredients:
                break
            print("Поле не може бути порожнім. Спробуйте ще раз.")

        while True:
            price = str(input("Введіть вартість: ")).strip()
            if price:
                break
            print("Поле не може бути порожнім. Спробуйте ще раз.")
        
    except Exception as e:
        print(f"Помилка: {e}")


    print(f"Дані:\n  {name}\n  {ingredients}\n  {price}")

    confirm = str(input("Підтвердити замовлення? (так/ні)")).strip().lower()

    if confirm == "так":
        query_add_user = f"""
            INSERT INTO {table_name} (Name, Ingredients, Price)
            VALUES (?, ?, ?);
        """
        cursor.execute(query_add_user, (name, ingredients, price))
        conn.commit()
        conn.close()
        print("Напій/десерт успішно додано!")
    else:
        print("Дію скасовано!")


def change_price():
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()

    try:
        while True:
            name = str(input("Введіть напій/десерт: ")).strip()
            if name:
                break
            print("Поле не може бути порожнім. Спробуйте знову.")
        
        while True:
            new_price = str(input("Введіть нову вартість: ")).strip()
            if new_price:
                break
            print("Поле не може бути пустим. Спробуйте знову.")

    except Exception as e:
        print(f"Помилка: {e}")


    query_upd_order = f"""
        UPDATE {table_name}
        SET Price = ?
        WHERE Name = ?;
    """

    cursor.execute(query_upd_order, (new_price, name))
    conn.commit()
    conn.close()
    print("Замовлення успішно оновлено!")


def change_ingredients():
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()

    try:
        while True:
            name = str(input("Введіть напій/десерт: ")).strip()
            if name:
                break
            print("Поле не може бути порожнім. Спробуйте знову.")
        
        while True:
            new_ingr = str(input("Введіть нові інгредієнти: ")).strip()
            if new_ingr:
                break
            print("Поле не може бути пустим. Спробуйте знову.")

    except Exception as e:
        print(f"Помилка: {e}")


    query_upd_order = f"""
        UPDATE {table_name}
        SET Ingredients = ?
        WHERE Name = ?;
    """

    cursor.execute(query_upd_order, (new_ingr, name))
    conn.commit()
    conn.close()
    print("Замовлення успішно оновлено!")


def delete_stuff():
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()

    name = str(input("Введіть назву напою/десерту: "))
    complete = input("Ви точно хочете видалити це? (так/ні): ").strip().lower()
    if complete == "так":
        query_dlt_client = f"""
            DELETE FROM {table_name}
            WHERE Name = ?;
        """
        cursor.execute(query_dlt_client, (name,))
        conn.commit()
        conn.close()
        print("Напій/десерт успішно видалено!")
    else:
        print("Дію скасовано!")


def menu():
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()

    query_cr_tb = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Name TEXT,
            Ingredients TEXT,
            Price TEXT
        );
    """
    cursor.execute(query_cr_tb)
    conn.commit()
    conn.close()

    while True:
        print("\nМеню:")
        print("1. Додати новий напій/десерт;")
        print("2. Змінити ціну напою/десерту;")
        print("3. Змінити інгредієнти напою/десерту;")
        print("4. Видалити напій/десерт;")
        print("0. Вихід.")
        try:
            choice = int(input("Оберіть дію (0-4): "))
        except Exception:
            print("Будь ласка, введіть число від 0 до 4.")
            continue


        if choice == 1:
            add_stuff()
        elif choice == 2:
            change_price()
        elif choice == 3:
            change_ingredients()
        elif choice == 4:
            delete_stuff()
        elif choice == 0:
            print("Роботу завершено.")
            break
        else:
            print("Такої опції не існує! Спробуйте ще раз.")



if __name__ == "__main__":
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()

    query_cr_tb = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Name TEXT,
            Ingredients TEXT,
            Price TEXT
        );
    """
    cursor.execute(query_cr_tb)
    conn.commit()
    conn.close()
    menu()