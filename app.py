import os

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import secrets
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
admin_app_password = os.getenv('ADMIN_APP_PASSWORD')

# Start app
app = Flask(__name__)

# app config
# locally
#app.config['MYSQL_HOST'] = 'localhost'

app.config['MYSQL_HOST'] = 'mysql'
app.config['MYSQL_USER'] = db_user
app.config['MYSQL_PASSWORD'] = db_password
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'flask'

# mysql connection
mysql = MySQL(app)

#Settings flush messages
app.secret_key = b'test_x44'

@app.route('/')
def index():
    create_tables()

    return render_template("index.html")


@app.route('/login', methods=["POST"])
def login():
    if request.method == 'POST':

        userid = int(request.form['userid'])
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT fullname FROM admin_users WHERE (user_id = %s AND password = %s)', (int(userid), password))
        fullname = cur.fetchall()
        if len(fullname) == 0:
            flash('An user with this user id and password is not found in the DB')
            return redirect(url_for('users_login'))
        else:
            session['logged_in'] = True
            return redirect(url_for('pizza_orders', name = fullname[0][0]))


@app.route('/pizzas_order_form')
def pizzas_order_form():
    return render_template("pizzas-order-form.html")

@app.route('/users_login')
def users_login():
    return render_template("users-login.html")

@app.route('/kill_session')
def kill_session():
    # Clear stored in the session object
    session.pop('logged_in', default=None)
    return render_template("users-login.html")


@app.route('/add_pizza', methods=["POST"])
def add_pizza():
    if request.method == 'POST':
        pizza = request.form['pizza']
        description = request.form['description']
        print(pizza, description)
        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO pizza (name, description) VALUES (%s, %s)', (pizza, description))
            mysql.connection.commit()
            flash('Pizza order added successfully')
            return redirect(url_for('pizzas_order_form'))
        except Exception as e:
            return redirect(url_for('index'))

@app.route('/pizza_orders/<name>', methods=['GET', 'POST'])
def pizza_orders(name):

    if 'logged_in' not in session:
        return render_template("users-login.html")
    else:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM pizza')
        pizzas = cur.fetchall()
        return render_template("pizza-orders.html", pizzas = pizzas, name = name)

def create_tables():

    try:
        cur = mysql.connection.cursor()

        # Create pizza table
        sql_pizza_table='''CREATE TABLE IF NOT EXISTS pizza(
        order_id INT NOT NULL AUTO_INCREMENT,
        name varchar(255) NOT NULL,
        description varchar(255) NOT NULL,
        PRIMARY KEY(`order_id`)
        )'''
        cur.execute(sql_pizza_table)

        # Start in 1000
        start_index_sql ='''ALTER TABLE pizza AUTO_INCREMENT = 1000'''
        cur.execute(start_index_sql)

        mysql.connection.commit()

    except Exception as e:
        if "ERROR" in str(e):
            exit("There are some failures in the DB")
        else:
            mysql.connection.commit()

    try:
        cur = mysql.connection.cursor()

        # Create admin_users table
        sql_users_table='''CREATE TABLE IF NOT EXISTS admin_users (
        user_id INT NOT NULL,
        fullname varchar(255) NOT NULL,
        role varchar(255) NOT NULL,
        password varchar(255) NOT NULL,
        PRIMARY KEY(`user_id`)
        )'''
        cur.execute(sql_users_table)

        mysql.connection.commit()

    except TypeError as e:
        if "ERROR" in str(e):
            exit("There are some failures in the DB")
        else:
            mysql.connection.commit()
    try:
        user_id = 1000
        fullname = "System administrator"
        role = "Admin"
        password = admin_app_password

        cur = mysql.connection.cursor()
        cur.execute('INSERT IGNORE INTO admin_users (user_id, fullname, role, password) VALUES (%s, %s, %s, %s)', (user_id, fullname, role, password))
        mysql.connection.commit()

    except Exception as e:
        if e:
            print("The operation cannot be executed")
            exit("There are some failures in the DB")
        else:
            mysql.connection.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000, debug = True)
