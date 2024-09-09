from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

# app config
app.config['MYSQL_HOST'] = 'mysql'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'flask'

# flush messages
app.secret_key = "secret key"

# mysql connection
mysql = MySQL(app)

#Settings
app.secret_key = b'test_x44'

@app.route('/')
def index():
    create_table()

    return render_template("index.html")

def create_table():

    try:
        cur = mysql.connection.cursor()

    # Create table
        sql='''CREATE TABLE pizza(
        order_id INT NOT NULL AUTO_INCREMENT,
        nombre varchar(255) NOT NULL,
        description varchar(255) NOT NULL,
        PRIMARY KEY(`order_id`)
        )'''
        cur.execute(sql)

    # Start in 1000
        start_index_sql ='''ALTER TABLE pizza AUTO_INCREMENT = 1000'''
        cur.execute(start_index_sql)

    except Exception as e:
        if "already exists" in str(e):
            return "pizza table is already created"
        else:
            mysql.connection.commit()

@app.route('/add_pizza', methods=["POST"])
def add_pizza():
    if request.method == 'POST':
        pizza = request.form['pizza']
        description = request.form['description']
        print(pizza, description)
        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO pizza (nombre, description) VALUES (%s, %s)', (pizza, description))
            mysql.connection.commit()
            flash('Pizza order added successfully')
            return redirect(url_for('index'))
        except Exception as e:
            print(e)
            return redirect(url_for('index'))

@app.route('/pizza_orders', methods=["POST"])
def pizza_orders():

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM pizza')
    pizzas = cur.fetchall()
    print(pizzas)
    return render_template("pizza-orders.html", pizzas = pizzas)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000, debug = True)
