from flask import Flask,send_from_directory, render_template, request, flash, session, url_for, redirect, make_response
from flask.ext.mail import Message, Mail
from flask.ext.socketio import SocketIO, emit,join_room,leave_room
from chat_foldre import app, socketio, thread
from chat_foldre.forms import ContactForm, SignupForm, SigninForm, ProfileForm
from models import db, User, User_list, Chat, Chat_list
from flask.ext.socketio import SocketIO
import json, time,datetime
import os
from threading import Thread
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

mail = Mail()

@app.route('/')
def home():
  session.clear()
  return redirect(url_for('signin'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/testdb')
def testdb():
  if db.session.query("1").from_statement("SELECT 1").all():
      a1=User_list.query.all()
      a=[k1[1] for k1 in a1]
      return render_template('testdb.html',l=a)
  else:
    return 'Something is broken.'

@app.route('/contact', methods=['GET', 'POST'])
def contact():
  form = ContactForm()

  if request.method == 'POST':
      if form.validate()==False:
          flash('All fields are required')
          return render_template('contact.html',form=form)
      else:
          msg = Message(form.subject.data, sender='savchenko.ilia@gmail.com', recipients=[form.email.data])
          msg.body = """
          From: %s <%s>
          %s
          """ % (form.name.data, form.email.data, form.message.data)
          mail.send(msg)
          return render_template('contact.html',success=True)

  elif request.method == 'GET':
    return render_template('contact.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  form = SignupForm()

  if 'email' in session:
    return redirect(url_for('profile'))

  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signup.html', form=form)
    else:
      newuser = User(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
      db.session.add(newuser)
      db.session.commit()

      session['email'] = newuser.email
      return redirect(url_for('profile'))
      #[1] Create a new user [2] sign in the user [3] redirect to the user's profile

  elif request.method == 'GET':
    return render_template('signup.html', form=form)

@app.route('/profile', methods=['GET','POST'])
def profile():
  email=session['email']
  global thread
  if thread is None:
      thread=Thread()
      thread.start()
  form=ProfileForm()

  user = User.query.filter_by(email = email).first()

  if user is None:
    return redirect(url_for('signup'))
  else:
    session['name']=user.firstname
    session['id']=user.uid
    '''u=User_list.query.filter_by(user_id=user.uid)'''
    '''c=db.session.query(Chat.msg.label('msg'),User.firstname.label('name')).filter(Chat.user_id==User.uid).filter(Chat.chat_id==b).order_by(Chat.time).all()'''
    u=db.session.query(User_list.chat_id.label('chat_id'),Chat_list.name.label('name')).filter(User_list.chat_id==Chat_list.chat_id).filter(User_list.user_id==user.uid).all()
    return render_template('profile.html', form=form,element=u)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
  form = SigninForm()
  emails=User.query.all()
  emails=[i.email for i in emails]
  if 'email' in emails:
    return redirect(url_for('profile'))

  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signin.html', form=form)
    else:
      session['email'] = form.email.data
      return redirect(url_for('profile'))

  elif request.method == 'GET':
    return render_template('signin.html', form=form)

@app.route('/signout')
def signout():

  if 'email' not in session:
    return redirect(url_for('signin'))

  session.pop('email', None)
  return redirect(url_for('home'))

def json_chat_msg(list):
    lst = []
    for pn in list:
        d = {}
        d['user_name']=pn.name
        d['msg']=pn.msg
        lst.append(d)
    return json.dumps(lst)

def json_room_list(list):
    lst=[]
    for pn in list:
        d={}
        d['chat_id']=pn.chat_id
        d['name']=pn.name
        lst.append(d)
    return json.dumps(lst)

def json_find_room(list):
    lst=[]
    for pn in list:
        d={}
        d['chat_id']=pn.chat_id
        d['name']=pn.name
        lst.append(d)
    return json.dumps(lst)

@socketio.on('my event', namespace='/test')
def test(message):
    b=int(message['data'])
    user_join_room(b)

def user_join_room(b):
    join_room(b)
    session['room'] = b
    c=db.session.query(Chat.msg.label('msg'),User.firstname.label('name')).filter(Chat.user_id==User.uid).filter(Chat.chat_id==b).order_by(Chat.time).all()
    emit('send_room_form_update',{'code': 1})
    emit('my response',{'data': json_chat_msg(c)})

@socketio.on('my room event', namespace='/test')
def send_room_msg(message):
    new_msg=Chat(session['id'],session['room'],message['data'],datetime.datetime.utcnow())
    db.session.add(new_msg)
    db.session.commit()
    emit('room msg', {'data':message['data'], 'user_name': session['name']},room=session['room'])

@socketio.on('add room', namespace='/test')
def add_room(message):
    new_room=Chat_list(message['data'])
    db.session.add(new_room)
    db.session.commit()
    add_room_to_user_list=User_list(session['id'],new_room.chat_id)
    db.session.add(add_room_to_user_list)
    db.session.commit()
    update_room_list()

@socketio.on('delete room', namespace='/test')
def add_room(message):
    b=int(message['data'])
    try:
        leave_room(b)
        if session['room'] == b:
            emit('send_room_form_update',{'code': -1})
        to_delete=User_list.query.filter_by(chat_id=b).first()
        db.session.delete(to_delete)
        db.session.commit()
        update_room_list()
    except IntegrityError:
        return False
    except:
        raise

@socketio.on('join room', namespace='/test')
def join_user_to_room(message):
    join_room(message['data'])
    user_room_list=db.session.query(User_list.chat_id).filter(User_list.chat_id==message['data']).filter(User_list.user_id==session['id']).all()
    if len(user_room_list) > 0:
        user_join_room(message['data'])
    else:
        #session['room']=message['data']
        add_room_to_user_list=User_list(session['id'],message['data'])
        try:
            db.session.add(add_room_to_user_list)
            db.session.commit()
            update_room_list()
            user_join_room(int(message['data']))
        except IntegrityError:
            return False
        except:
            raise


@socketio.on('find room', namespace='/test')
def find_room(message):
    room_list=Chat_list.query.all()
    list_of_rooms=[]
    for i in room_list:
        if message['data'] in i.name:
            list_of_rooms.append(i)
    emit('find room result',{'data': json_find_room(list_of_rooms)})

def update_room_list():
    '''u=User_list.query.filter_by(user_id=session['id'])
    c=db.session.query(Chat.msg.label('msg'),User.firstname.label('name')).filter(Chat.user_id==User.uid).filter(Chat.chat_id==b).order_by(Chat.time).all()'''
    u=db.session.query(User_list.chat_id.label('chat_id'),Chat_list.name.label('name')).filter(User_list.chat_id==Chat_list.chat_id).filter(User_list.user_id==session['id']).all()
    emit('update room list', {'data': json_room_list(u)})