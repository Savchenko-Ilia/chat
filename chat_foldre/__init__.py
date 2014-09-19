from gevent import monkey
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
monkey.patch_all()
from flask import Flask
from threading import Thread
from flask.ext.heroku import Heroku
import os
from flask.ext.socketio import SocketIO

app = Flask(__name__)

app.secret_key = 'development key'
app.debug=True

socketio=SocketIO(app)
thread=None

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'contact@example.com'
app.config["MAIL_PASSWORD"] = 'your-password'
app.config["PORT"]=5000

from routes import mail
mail.init_app(app)



#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:4893541@127.0.0.1/development'
#app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:4893541@127.0.0.1/development'
#heroku = Heroku(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

'''from models import db
db.init_app(app)'''

db = SQLAlchemy(app)
#db.apply_pool_defaults()

class User(db.Model):
  __tablename__ = 'users'
  uid = db.Column(db.Integer, primary_key = True)
  firstname = db.Column(db.String(100))
  lastname = db.Column(db.String(100))
  email = db.Column(db.String(120), unique=True)
  pwdhash = db.Column(db.String(150))

  def __init__(self, firstname, lastname, email, password):
    self.firstname = firstname.title()
    self.lastname = lastname.title()
    self.email = email.lower()
    self.set_password(password)

  def set_password(self, password):
    self.pwdhash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.pwdhash, password)

class User_list(db.Model):
    __tablename__='user_list'
    user_id=db.Column(db.Integer(unsigned=True),db.ForeignKey('users.uid'), primary_key=True)
    #chat_id=db.Column(db.SmallInteger, db.ForeignKey('chat_list.chat_id'), primary_key=True)
    chat_id=db.Column(db.Integer, db.ForeignKey('chat_list.chat_id'), primary_key=True)
    '''chat=db.relation("Chat_list",backref="user_list")'''

    def __init__(self,user_id,chat_id):
        self.user_id=user_id
        self.chat_id=chat_id

class Chat_list(db.Model):
    __tablename__='chat_list'
    #chat_id=db.Column(db.SmallInteger, primary_key=True)
    chat_id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(40))

    def __init__(self,name):
        self.name=name.title()

class Chat(db.Model):
    __tablename__='chat'
    user_id=db.Column(db.Integer(), db.ForeignKey('users.uid'), primary_key=True)
    #chat_id=db.Column(db.SmallInteger, db.ForeignKey('chat_list.chat_id'), primary_key=True)
    chat_id=db.Column(db.Integer, db.ForeignKey('chat_list.chat_id'), primary_key=True)
    msg=db.Column(db.String(155))
    time=db.Column(db.TIMESTAMP, primary_key=True)

    def __init__(self, user_id,chat_id,msg,time):
        self.user_id=user_id
        self.chat_id=chat_id
        self.msg=msg.title()
        self.time=time

import chat_foldre.routes