import flask
import flask_mysqldb
import pubnub
import uuid
from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL, MySQLdb

from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pprint import pprint

app = Flask(__name__)
app.secret_key = "AzurCam123"
# yX6dCdPZF9ggdQ2kHPGA
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "azurcam"

db = MySQL(app)


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
            cursor.execute("SELECT * FROM users WHERE email=%s AND password =%s", (email, password))
            info = cursor.fetchone()

            if info is not None:
                if info['email'] == email and info['password'] == password:
                    #save variables
                    session['loginsuccess'] = True
                    session['user_id'] = info['user_id']
                    session['name'] = info['name']
                    session['username'] = info['username']
                    session['email'] = info['email']
                    session['iot_id'] = info['iot_id']
                    return redirect(url_for('home'))
            else:
                print("Failed Login")
                return redirect(url_for('index'))

    return render_template("index.html")


@app.route("/account")
def account():
    if session['loginsuccess']:
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

            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("INSERT INTO azurcam.users(name, username, email, password)VALUES(%s, %s, %s, %s)",
                           (name, username, email, password))

            db.connection.commit()
            return redirect(url_for('index'))
    return render_template("registration.html")


@app.route('/home')
def home():
    if session['loginsuccess']:
        iot_id = session['iot_id']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "SELECT * FROM images WHERE image_reference LIKE '%s%%' " % iot_id
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


"""
RECIEVING DETECTED MOTION FROM PUBNUB
"""


class MySubscribeCallback(SubscribeCallback):
    def message(self, pubnub, message):
        messageArray = message.__dict__
        print(messageArray['message']['sender'])
        cursor = db.cursor()
        cursor.execute("INSERT INTO azurcam.users(name, username, email, password)")


pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-60d39bd0-5cfb-11ec-96e9-32997ff5e1b9"
pnconfig.publish_key = "pub-c-0586af82-d21f-4eb0-a261-9b0ec1e03ba0"

pubnub = PubNub(pnconfig)

pubnub.add_listener(MySubscribeCallback())

pubnub.subscribe().channels("azurcam-channel").with_presence() \
    .execute()

if __name__ == '__main__':
    app.run()
