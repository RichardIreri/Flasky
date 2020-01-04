""" Application's models. """

from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager

# Role and user model definition
class Role(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    # String representation for debugging and testing
    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin,db.Model):
    # Loading the UserMixin class that implements default flask_login properties or methods.
    # Update to the User model to support user login.
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))      # Password hash attribute to store password hashes

    # Passward hashing in the user model
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # User loader function.
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # String representation for debugging and testing
    def __repr__(self):
        return '<User %r>' % self.username 

