from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL, MySQLdb

app = Flask(__name__)
app.secret_key = "AzurCam123"
#yX6dCdPZF9ggdQ2kHPGA
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "azurcam"

db = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM users WHERE email=%s AND password =%s", (email, password))
            info = cursor.fetchone()
            print(info)
            if info is not None:
                if info['email'] == email and info['password'] == password:
                    session['loginsuccess'] = True
                    return redirect(url_for('profile'))
            else:
                print("Failed Login")
                return redirect(url_for('index'))

    return render_template("account.html")


@app.route("/account")
def account():
    return render_template("account.html")


@app.route('/new', methods=['GET', 'POST'])
def registration():
    if request.method == "POST":
        if "one" in request.form and "two" in request.form and "three" in request.form:
            username = request.form['one']
            email = request.form['two']
            password = request.form['three']
            cur = db.connection.cursor(MySQLdb.DictCursor)
            cur.execute("INSERT INTO azurcam.users(username, email, password)VALUES(%s, %s, %s)",
                        (username, email, password))
            db.connection.comit()
            return redirect(url_for('index'))
    return render_template("registration.html")


@app.route('/new/profile')
def profile():
    #  if session['loginsuccess'] == True:
    return render_template("profile.html")


@app.route('/home')
def home():
    print("A")
    #  if session['loginsuccess'] == True:
    return render_template("home.html")


@app.route('/new/logout')
def logout():
    session.pop('loginsuccess', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
