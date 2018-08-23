from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash, request, current_app, make_response
from flask_login import login_required, current_user

from . import main
from .forms import PostForm, EditProfileForm, EditProfileAdminForm, CommentForm
from .. import db
from ..models import User, Permission, Post, Comment
from ..decorators import admin_required, permission_required

@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    show_followed = False
    if current_user.can(Permission.WRITE_ARTICLES) and \
        form.validate_on_submit():
            post = Post(body=form.body.data, author=current_user._get_current_object())
            db.session.add(post)
            return redirect(url_for('.index'))
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.jinja', 
                    form=form, 
                    posts=posts,
                    pagination=pagination,
                    show_followed = show_followed)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.jinja', user=user, posts=posts)

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

@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment()
    post = Post.query.get_or_404(id)
    return render_template('post.jinja', posts=[post])

@main.route('/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
        not current_user.can(Permission.ADMINSTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=id))
    form.body.data = post.body
    return render_template('edit_post.jinja', form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    current_user.follow(user)
    return redirect(url_for('.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    current_user.unfollow(user)
    return redirect(url_for('.user', username=username))

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOW_PER_PAGE'],
        error_out=False)
    follows = ({'user':item.follower, 'timestamp':item.timestamp} 
                for item in pagination.items)
    return render_template('followers.jinja', user=user, title="Followers of",
                            endpoint='.followers', pagination=pagination,
                            follows=follows)

@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOW_PER_PAGE'],
        error_out=False)
    follows = ({'user':item.followed, 'timestamp':item.timestamp} 
                for item in pagination.items)
    return render_template('followers.jinja', user=user, title="Followed by",
                            endpoint='.followers', pagination=pagination,
                            follows=follows)

@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp