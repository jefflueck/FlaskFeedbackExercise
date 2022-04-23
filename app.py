from flask import Flask, request, render_template, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
db = SQLAlchemy()


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', "postgresql:///flask_feedback")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

# the toolbar is only enabled in debug mode:
app.debug = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# set a 'SECRET_KEY' for heroku to work
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'thisisthedefaultsecret')

toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.drop_all()
db.create_all()


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
    '''create new user and hash password with our register class method'''
    user = User.register(username, password, email, first_name, last_name)
    db.session.add(user)

    try:
      '''commit the data to the database'''
      db.session.commit()
    except IntegrityError:
      '''if the username already exists, flash an error message and re-render the form'''
      flash(f'Username {username} already exists!')
      return render_template('/register.htm', form=form)
    '''if valid set username in session and redirect to secret page'''
    session['username'] = user.username
    flash(f'Account created for {username}!')
    return redirect(f'/users/{user.username}')

  return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login_process():
  '''Process login form'''
  form = LoginForm()
  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    '''check using our authenticate class methood if the user exists in the database'''
    user = User.authenticate(username, password)
    if user:
      flash(f'Welcome, {username}!')
      '''set the username in the session and redirect to the secret page'''
      session['username'] = user.username
      return redirect(f"/users/{user.username}")
    if user not in User.query.all():
      flash('User does not exist! Please register.')
      return redirect('/register')

  return render_template('login.html', form=form)

@app.route('/users/<username>')
def show_user(username):
  '''Show user profile'''
  user = User.query.filter_by(username=username).first()
  feedbacks = Feedback.query.filter_by(username=username).all()
  if user and session['username'] == username:
    return render_template('user.html', user=user, feedbacks=feedbacks)
  else:
    flash(f'User {username} not found or not logged in!')
    return redirect('/login')

@app.route('/users/<username>/delete', methods=['GET','POST'])
def delete_user(username):
  '''Delete user'''
  user = User.query.filter_by(username=username).first()
  db.session.delete(user)
  db.session.commit()
  flash(f'User {username} deleted!')
  return redirect('/login')


@app.route('/users/<username>/feedback/add', methods=['GET','POST'])
def post_feedback(username):
  '''Add feedback'''
  if 'username' not in session:
    flash(f'You have to be logged in to see this page!')
    return redirect('/login')
  form = FeedbackForm()
  if form.validate_on_submit():
    title = form.title.data
    content = form.content.data
    feedback = Feedback(title=title, content=content, username=username)
    db.session.add(feedback)
    db.session.commit()
    flash(f'Feedback added!')
    return redirect(f'/users/{username}')
  return render_template('add_feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET','POST'])
def update_feedback(feedback_id):
  '''Update feedback'''
  feedback = Feedback.query.get_or_404(feedback_id)
  if 'username' not in session:
    flash(f'You have to be logged in to see this page!')
    return redirect('/login')
  form = FeedbackForm()
  if form.validate_on_submit():
    feedback.title = form.title.data
    feedback.content = form.content.data
    db.session.commit()
    flash(f'Feedback updated!')
    return redirect(f'/users/{feedback.username}')
  return render_template('update_feedback.html', form=form, feedback=feedback)

@app.route('/feedback/<int:feedback_id>/delete', methods=['GET','POST'])
def delete_feedback(feedback_id):
  '''Delete feedback'''
  feedback = Feedback.query.get_or_404(feedback_id)
  if 'username' not in session:
    flash(f'You have to be logged in to see this page!')
    return redirect('/login')
  db.session.delete(feedback)
  db.session.commit()
  flash(f'Feedback deleted!')
  return redirect(f'/users/{feedback.username}')

@app.route('/logout')
def logout():
  '''Logout'''
  session.pop('username')
  flash('Logged out!')
  return redirect('/')





# No longer using this code
@app.route('/secret')
def secret():
  '''Secret page'''
  if 'username' not in session:
    flash(f'You have to be logged in to see this page!')
    return redirect('/login')
  return render_template('secret.html')
