from flask import Flask, session, render_template, request, flash, redirect, url_for
from getdata import get_desserts, get_drinks
from databases.db_fav import fav_table
from databases.db_cart import cart_table
from databases.db_order import orders_table
import sqlite3
import time
import random
from threading import Thread


app = Flask(__name__)

app.config['SECRET_KEY'] = "VeryFrickingStrongSigmaUltraKey"


@app.route("/")
def index():
    return render_template("index.html", logged_in='user' in session)


@app.route("/menu")
def menu():
    if 'user' not in session:
        return redirect(url_for('login'))
    drinks = get_drinks()
    deserts = get_desserts()

    user_id = session['user']['id']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    favorites_query = f"""
        SELECT name FROM favorites_{user_id};
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(favorites_query)
    favorites = [row[0] for row in cursor.fetchall()]   # getting name to check if the item is in favorites
    conn.close()
    return render_template("menu.html", drinks=drinks, deserts=deserts, favorites=favorites)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phonenum = request.form.get("phonenum")
        password = request.form.get("password")

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        query_ch_exs = """
            SELECT * FROM users 
            WHERE PhoneNum = ?; 
        """
        cursor.execute(query_ch_exs, (phonenum,))
        user_exists = cursor.fetchone()
        
        if user_exists:
            query_ch_ps = """
                SELECT * FROM users
                WHERE PhoneNum = ? AND Password = ?;
            """
            cursor.execute(query_ch_ps, (phonenum, password))
            password_check = cursor.fetchone()

            if password_check:
                session['user'] = {'id': user_exists[0]}  # if password is correct, saving user in session
                flash("Success!", "success")
                return redirect(url_for('profile'))  
            else:
                flash("Incorrect password!", "warning")
                return render_template("login.html") 
        
    return render_template("login.html", logged_in='user' in session)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    # getting information user wrote
    if request.method == 'POST':
        name = request.form.get("name")
        phonenum = request.form.get("phonenum")
        age = request.form.get("age")
        password = request.form.get("password")

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # checking if user exists by phonenumber
        query_ch_exs = """
            SELECT * FROM users 
            WHERE PhoneNum = ?; 
        """
        cursor.execute(query_ch_exs, (phonenum,))
        user_exists = cursor.fetchone()
        
        if user_exists:
            flash("Account already exists!", "danger")
            return redirect(url_for('login'))  
        else:
            # if the user doesn't exist, we put him in database of users
            query_insr = """
                INSERT INTO users (Name, PhoneNum, Age, Password)
                VALUES (?, ?, ?, ?);
            """
            cursor.execute(query_insr, (name, phonenum, age, password))
            conn.commit()
            # creating a session with this user saving his id. we will identificate and get info about him by id.
            session['user'] = {'id': cursor.lastrowid} 
            
            user_id = cursor.lastrowid
            # creating unique favorites, cart and orders tables
            fav_table(user_id)  
            cart_table(user_id)
            orders_table(user_id)

            conn.close()
            return redirect(url_for('index'))  
         
    return render_template("signup.html", logged_in='user' in session)


@app.route("/profile")
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['id']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # getting user's info by his id
    query_user_info = """
        SELECT * FROM users 
        WHERE Id = ?;
    """
    cursor.execute(query_user_info, (user_id,))
    user_data = cursor.fetchone()

    if not user_data:
        flash("user not found!", "danger")
        return redirect(url_for("logout"))

    conn.commit()
    conn.close()
    # saving his info in a dict to display (name, phone number and age)
    user_info = {
        'name': user_data[1],
        'phone': user_data[2],
        'age': user_data[3]
    }

    return render_template("profile.html", user=user_info)


@app.route("/logout")
def logout():
    session.pop('user', None) 
    flash("You logout of your profile!", "info")
    return redirect(url_for('index'))


@app.route('/add_to_favorites', methods=['POST', 'GET'])
def add_to_favorites():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    name = request.form.get("name")
    ingredients = request.form.get("ingredients")
    price = request.form.get("price")

    fav_table(user_id)

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM favorites_{user_id};")
    count = cursor.fetchone()[0]

    if count >= 6:
        conn.close()
        flash("You can't add more than 6 items to your favorites.")
        return redirect(url_for('menu'))

    query_check = f"""
        SELECT * FROM favorites_{user_id} WHERE name = ?;
    """
    cursor.execute(query_check, (name,))
    item = cursor.fetchone()

    if not item:
        query = f"""
        INSERT INTO favorites_{user_id} (name, ingredients, price)
        VALUES (?, ?, ?);
        """
        cursor.execute(query, (name, ingredients, price))
        conn.commit()

    conn.close()

    favorites_query = f"""
        SELECT name FROM favorites_{user_id};
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(favorites_query)
    favorites = [row[0] for row in cursor.fetchall()]  # getting name to check if the item is in favorites
    conn.close()
    
    return render_template('menu.html', drinks=get_drinks(), deserts=get_desserts(), favorites=favorites)


@app.route("/fav", methods=["GET", "POST"])
def favorites():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    query = f"""
    SELECT * FROM favorites_{user_id};
    """
    cursor.execute(query)
    favorites = cursor.fetchall()
    conn.close()

    return render_template("fav.html", favorites=favorites)


@app.route('/remove_from_favorites', methods=['POST'])
def remove_from_favorites():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    name = request.form.get("name")

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    query = f"""
    DELETE FROM favorites_{user_id} WHERE name = ?;
    """
    cursor.execute(query, (name,))
    conn.commit()
    conn.close()

    return redirect(url_for('menu'))


@app.route("/add_tocart", methods=["GET", "POST"])
def add_to_cart():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    name = request.form.get("name")
    ingredients = request.form.get("ingredients")
    price = request.form.get("price")

    cart_table(user_id)

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM cart_{user_id};")
    count = cursor.fetchone()[0]

    query_check = f"""
        SELECT * FROM favorites_{user_id} WHERE name = ?;
    """
    cursor.execute(query_check, (name,))
    item = cursor.fetchone()

    if not item:
        query = f"""
        INSERT INTO cart_{user_id} (name, ingredients, price)
        VALUES (?, ?, ?);
        """
        cursor.execute(query, (name, ingredients, price))
        conn.commit()

    conn.close()
    
    return render_template('menu.html', drinks=get_drinks(), deserts=get_desserts())


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    name = request.form.get("name")

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    query = f"""
    DELETE FROM cart_{user_id} WHERE name = ?;
    """
    cursor.execute(query, (name,))
    conn.commit()
    conn.close()

    return redirect(url_for('cart'))


@app.route("/cart", methods=["GET", "POST"])
def cart():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['id']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    query = f"""
    SELECT * FROM cart_{user_id};
    """
    cursor.execute(query)
    cart = cursor.fetchall()
    conn.close()

    return render_template("cart.html", cart=cart)


@app.route("/order_page", methods=["GET", "POST"])
def order_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    name = request.form.get('name')
    price = request.form.get('price')

    return render_template("order.html", name=name, price=price)


@app.route("/ordered", methods=["GET", "POST"])
def ordered():
    name = request.form.get('name')
    price = request.form.get('price')

    user_id = session['user']['id']
    orders_table(user_id)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # delete item from cart after user ordered it
    query = f"""
    DELETE FROM cart_{user_id} WHERE name = ?;
    """
    cursor.execute(query, (name,))
    conn.commit()

    cart_table(user_id)

    query_phonenum = """
        SELECT PhoneNum FROM users
        WHERE Id = ?;
    """
    cursor.execute(query_phonenum, (user_id,))
    phonenum = cursor.fetchone()[0]

    # picking random time within which the drink/dessert will be ready
    duration_proccess = random.randint(5, 15)
    time_created = int(time.time())

    query = f"""
        INSERT INTO orders_{user_id} (name, price, phonenum, time, time_created)
        VALUES (?, ?, ?, ?, ?);
    """
    cursor.execute(query, (name, price, phonenum, duration_proccess, time_created))
    conn.commit()

    query_id = f"""
        SELECT id FROM orders_{user_id}
        WHERE phonenum = ?;
    """
    cursor.execute(query_id, (phonenum,))
    order_id = cursor.fetchone()[0]

    query_time = f"""
        SELECT time FROM orders_{user_id}
        WHERE phonenum = ?;
    """
    cursor.execute(query_time, (phonenum,))
    time_order = cursor.fetchone()[0]
    conn.close()

    return render_template("ordered.html", order_id=order_id, time_order=time_order, name=name)


@app.route("/yourord", methods=["GET", "POST"])
def your_orders():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = session['user']['id']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # getting users unique orders
    query = f"""
    SELECT * FROM orders_{user_id};
    """
    cursor.execute(query)
    orders = cursor.fetchall()
    conn.close()

    # ready or not status for every user and their item
    order_statuses = {}

    for order in orders:
        order_id = order[0]
        order_time = order[4]  # the time when order was made
        
        current_time = int(time.time())  # current time
        time_elapsed = current_time - order[5]

        if time_elapsed >= order_time * 60:  # checking if the time set for item to be done had elapsed
            status = True
        else:
            status = False

        order_statuses[order_id] = status

    return render_template("your_orders.html", orders=orders, order_statuses=order_statuses)


@app.route("/remove_order", methods=["GET", "POST"])
def remove_order():
    user_id = session['user']['id']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    order_id = request.form.get("id")
    
    query = f"""
    DELETE FROM orders_{user_id} WHERE id = ?;
    """
    cursor.execute(query, (order_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('your_orders'))


if __name__ == '__main__':
    app.run(debug=True)
