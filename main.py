from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb

app = Flask(__name__)
app.secret_key = "123456"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "azurcam"

db = MySQL(app)



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM users WHERE email=%s AND password =%s", (username,password))
            info = cursor.fetchone()
            print(info)
            if info is not None:
                if info['email'] == username and info['password'] == password:
                    session['loginsuccess'] = True
                    return redirect(url_for('profile'))
            else:
               return redirect(url_for('index'))

    return render_template("login.html")


@app.route('/new', method=['GET', 'POST'])
def new_user():
    if request.method == "POST":
        if "one" in request.form and "two" in request.form and "three" in request.form:
            username = request.form['one']
            email = request.form['two']
            password = request.form['three']
            cur = db.connection.cursor(MySQLdb.DictCursor)
            cur.execute("INSERT INTO azurcam.users(username, email, password)VALUES(%s, %s, %s)",(username, email, password))
            db.connection.comit()
            return redirect(url_for('index'))
    return render_template("register.html")
@app.route('/new/profile')
def profile():
    if session['loginsuccess'] == True:
        return render_template("profile.html")

@app.route('/new/logout')
def logout():
    session.pop('loginsuccess',None)
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)


# @app.route('/new')
# def new_user():
#     return render_template("register.html")
#
# @app.route('/profile')
# def profile():
#     return render_template("profile.html")
#
# if __name__ == '__main__':
#     app.run(debug=True)