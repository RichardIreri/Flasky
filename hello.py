# Rendering templates
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message

# Application and extensions initializations
app = Flask(__name__)           # Creating an application instance
bootstrap = Bootstrap(app)      # Initializing bootstrap
moment = Moment(app)            # Initializing moment
db = SQLAlchemy(app)            # Initializing database
migrate = Migrate(app, db)      # Initializing migrate
mail = Mail(app)                # Initializing mail

basedir = os.path.abspath(os.path.dirname(__name__)) # Create database path name

# Forms configuration
app.config['SECRET_KEY'] = 'hard to guess string'

# Configurations(Flask, Extensions and Application)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'family.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail configuration for Gmail
app.config['DEBUG'] = True
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                    sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)

# Form class definition
class NameForm(FlaskForm):
    name = StringField('What is you name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Handle a web form with GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def index(): 
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User',
                            'mail/new_user', user=user)
        else: # User exists
            session['known'] = True
        session['name'] = form.name.data 
       form.name.data = ''
        return redirect(url_for('index'))  # Redirect and user session
    return render_template('index.html', form=form, name=session.get('name'),
                            known=session.get('known', False), current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500 

# Adding a shell context
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, User=User)

# Role and user model definition
class Role(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    # String representation for debugging and testing
    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # String representation for debugging and testing
    def __repr__(self):
        return '<User %r>' % self.username 

if __name__=='__main__':
    app.run()