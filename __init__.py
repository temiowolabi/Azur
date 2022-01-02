import bcrypt
from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL, MySQLdb
from mysql.connector import connect, Error
from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

app = Flask(__name__)
app.secret_key = "AzurCam123"
# yX6dCdPZF9ggdQ2kHPGA
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "azurcam"

db = MySQL(app)
print(db)

pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-60d39bd0-5cfb-11ec-96e9-32997ff5e1b9"
pnconfig.publish_key = "pub-c-0586af82-d21f-4eb0-a261-9b0ec1e03ba0"

pubnub = PubNub(pnconfig)
alive = 0
data = {}


@app.route('/', methods=['GET', 'POST'])
def index():
    session['loginsuccess'] = False
    if request.method == 'POST':
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "SELECT * FROM users WHERE email= '%s'" % email
            print(sql)
            cursor.execute(sql)
            info = cursor.fetchone()

            if info is not None:
                hashed = info['password']
                print(hashed)
                if info['email'] == email and bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')):
                    # save variables
                    session['loginsuccess'] = True
                    session['user_id'] = info['user_id']
                    session['name'] = info['name']
                    session['password'] = info['password']
                    session['username'] = info['username']
                    session['email'] = info['email']
                    session['iot_id'] = info['iot_id']
                    return redirect(url_for('home'))
            else:
                print("Failed Login")
                return redirect(url_for('index'))

    return render_template("index.html")


@app.route("/account", methods=['GET', 'POST'])
def account():
    if session['loginsuccess']:
        print("a")
        if request.method == "POST":

            if "name" in request.form and "username" in request.form and "email" in request.form and "password" in request.form:
                name = request.form['name']
                username = request.form['username']
                username2 = session['username']
                email = request.form['email']

                cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("UPDATE azurcam.users SET name = %s, username = %s, email = %s WHERE "
                               "username = %s", (name, username, email, username2))
                db.connection.commit()
                return redirect(url_for('index'))
        return render_template("account.html")
    else:
        (print("Not Signed In"))
        return render_template("index.html")


@app.route('/new', methods=['GET', 'POST'])
def registration():
    if request.method == "POST":
        if "name" in request.form and "username" in request.form and "email" in request.form and "password" in request.form:
            name = request.form['name']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("INSERT INTO azurcam.users(name, username, email, password)VALUES(%s, %s, %s, %s)",
                           (name, username, email, hashed))

            db.connection.commit()
            return redirect(url_for('index'))
    return render_template("registration.html")


@app.route('/home')
def home():
    if session['loginsuccess']:
        iot_id = session['iot_id']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "SELECT * FROM images WHERE image_reference LIKE '%s-%%' " % iot_id
        print(sql)
        cursor.execute(sql)
        info = cursor.fetchall()
        array = []
        for ino in info:
            array.append(ino["image_reference"])
        return render_template("home.html", array=array)
    else:
        (print("Not Signed In"))
        return render_template("index.html")


@app.route('/help')
def helper():
    if session['loginsuccess']:
        return render_template('help.html')
    else:
        (print("Not Signed In"))
        return render_template("index.html")


@app.route('/new/logout')
def logout():
    session['loginsuccess'] = False
    return redirect(url_for('index'))


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if session['loginsuccess']:
        if request.method == 'POST':
            if 'iot_id' in request.form:
                username = session['username']
                iot_id = request.form['iot_id']

                cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                sql = "UPDATE users SET iot_id = '%s' WHERE username = '%s'" % (iot_id, username)
                cursor.execute(sql)
                db.connection.commit()
                session['iot_id'] = iot_id
            return redirect(url_for('home'))
        else:
            return render_template('setup.html')
    # salt
    else:
        (print("Not Signed In"))
        return render_template("index.html")


"""
RECIEVING DETECTED MOTION FROM PUBNUB
"""


class MySubscribeCallback(SubscribeCallback):
    def message(self, pubnub, message):
        messageArray = message.__dict__
        image_reference = messageArray['message']['image-reference']
        update_query = "INSERT INTO images (image_reference) VALUES ('%s')" % image_reference
        print(update_query)
        try:
            with connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="azurcam"
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(update_query)
                    connection.commit()
        except Error as e:
            print(e)


pubnub.add_listener(MySubscribeCallback())

pubnub.subscribe().channels("azurcam-channel").with_presence() \
    .execute()

if __name__ == '__main__':
    app.run(debug=True)
