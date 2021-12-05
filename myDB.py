from flask_sqlalchemy import SQLAlchemy

from .__init__ import db

class userTable(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String())
    phone_number = db.Column(db.String())
    password = db.Column(db.String())

    def __init__(self, name, email, phone_number, password):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.password = password


