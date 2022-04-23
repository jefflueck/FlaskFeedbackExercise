import bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
  db.app = app
  db.init_app(app)


class User(db.Model):
  '''users table'''
  __tablename__ = 'users'
  username = db.Column(db.String(20),primary_key=True, unique=True, nullable=False)
  password = db.Column(db.Text(), nullable=False)
  email = db.Column(db.String(50), unique=True, nullable=False)
  first_name = db.Column(db.String(30), nullable=False)
  last_name = db.Column(db.String(30), nullable=False)
  feedback = db.relationship('Feedback', backref='user', cascade='all,delete')


  @classmethod
  def register(cls, username, password, email, first_name, last_name):
    '''register user and hash password'''
    hashed = bcrypt.generate_password_hash(password)
    hashed_utf8 = hashed.decode('utf8')
    '''return instance of user with username and hashed password'''
    return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

  @classmethod
  def authenticate(cls, username, password):
    '''authenticate user and return user if valid, else return False'''
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
      return user
    else:
      return False

class Feedback(db.Model):
  '''feedback table'''
  __tablename__ = 'feedback'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  title = db.Column(db.String(100), nullable=False)
  content = db.Column(db.Text(), nullable=False)
  username = db.Column(db.String(20), db.ForeignKey('users.username'), nullable=False)


  def __repr__(self):
    return f'<Feedback id={self.id} title={self.title}>'


  def __repr__(self):
    '''show info about user when printed'''
    return f"<User object: {self.username}>"
