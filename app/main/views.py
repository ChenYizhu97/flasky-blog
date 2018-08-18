from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash
from flask_login import login_required, current_user

from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User
from ..decorators import admin_required

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_mail(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.jinja', 
                    form=form, 
                    name=session.get('name'), 
                    known=session.get('known', False))

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.jinja', user=user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        current_user.location = form.location.data
        db.session.add(current_user)
        flash('Your profile has been updated')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.about_me.data = current_user.about_me
    form.location.data = current_user.location
    return render_template('edit_profile.jinja', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user = user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = form.role.data
        user.location = form.location.data
        user.name = form.name.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.location.data = user.location
    form.role.data = user.role
    form.name.data = user.name
    form.about_me.data = user.about_me
    form.confirmed = user.confirmed
    return render_template('edit_profile.jinja', form=form, user=user)