""" Application routes in the main blueprint. """

from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app, flash
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from .. import db, mail 
from ..models import User 
from ..emails import send_email
from flask_mail import Message
from flask_login import login_required, current_user
from ..decorators import admin_required

#@main.route('/')
#def notify():
#    msg = Message('Hey there', sender='balozikeirano@gmail.com',
#                    recipients=['fiyey36770@wmail1.com', 'richardireri19@gmail.com'])
    #msg.body = 'Here is the body'
#    msg.html = '<b>This is a test email sent from richard\'s app. You don\'t have to reply.</b>'
#    mail.send(msg)

#    return 'Message has been sent'

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if current_app.config['FLASKY_ADMIN']:
                send_email(current_app.config['FLASKY_ADMIN'], 'New User',
                            'mail/new_user', user=user)
        else: # User exists
            session['known'] = True
        session['name'] = form.name.data 
        form.name.data = ''
        return redirect(url_for('.index'))  # Redirect and user session
    return render_template('index.html', form=form, name=session.get('name'),
                            known=session.get('known', False), current_time=datetime.utcnow())

# Profile page route
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

# Edit profile route for regular users
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)
    
# Edit profile route for administators
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = User.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
    

