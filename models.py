import bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


engine = create_engine('postgresql:///flask_feedback')
if not database_exists(engine.url):
    create_database(engine.url)

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

  @classmethod
  def register(cls, username, password, email, first_name, last_name):
    hashed = bcrypt.generate_password_hash(password)
    hashed_utf8 = hashed.decode('utf8')
    return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

  @classmethod
  def authenticate(cls, username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
      return user
    else:
      return False

  def __repr__(self):
    return f"<User object: {self.username}>"
