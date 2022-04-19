from flask import Flask, request, render_template, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///flask_feedback"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

# the toolbar is only enabled in debug mode:
app.debug = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = 'The secret key'
toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.drop_all()
# db.create_all()


@app.route('/')
def index():
  '''Homepage'''
  return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register_process():
  '''Process registration form'''
  form = RegisterForm()

  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    email = form.email.data
    first_name = form.first_name.data
    last_name = form.last_name.data
    user = User.register(username, password, email, first_name, last_name)
    db.session.add(user)

    try:
      db.session.commit()
    except IntegrityError:
      flash(f'Username {username} already exists!')
      return render_template('/register.html', form=form)
    session['username'] = user.username
    flash(f'Account created for {username}!')
    return redirect('/secret')

  return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login_process():
  '''Process login form'''
  form = LoginForm()
  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data

    user = User.authenticate(username, password)
    if user:
      flash(f'Welcome, {username}!', 'success')
      session['username'] = user.username
      return redirect('/secret')
    else:
      flash('Invalid credentials!')
  else:
    return render_template('login.html', form=form)

@app.route('/secret')
def secret():
  '''Secret page'''
  if 'username' not in session:
    flash(f'You have to be logged in to see this page!')
    return redirect('/login')
  return render_template('secret.html')

@app.route('/logout')
def logout():
  '''Logout'''
  session.pop('username')
  flash('Logged out!', 'success')
  return redirect('/')
