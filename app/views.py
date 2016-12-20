from app import app
from flask import render_template, url_for, redirect, flash, request
from .forms import LoginForm, RegisterForm, PostForm, ProfileForm, CommentForm
from app.models import User, Post, Follow, Comment
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc
from datetime import datetime
from app import db


@app.route('/', methods=['post', 'get'])
@app.route('/index', methods=['post', 'get'])
def index():
    form = PostForm()
    posts = list()
    if current_user.is_authenticated:
        posts = current_user.posts.all()
        follows = current_user.followed.all()
        for follow in follows:
            posts += User.query.get(follow.followed_id).posts.all()
        for post in posts:
            if post.timestamp is None:
                post.timestamp = datetime.utcnow()
                db.session.add(post)
                db.session.commit()
        posts.sort(key=lambda p:p.timestamp, reverse=True)

    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data)
        form.title.data = ''
        form.body.data = ''
        post.author = current_user
        db.session.add(post)
        db.session.commit()
        flash('You post microblog "%s" just now' % post.title)
        return redirect(url_for('blogs', username=current_user.username))
    return render_template('index.html', form=form, posts=posts)


@app.route('/register', methods=['post', 'get'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()
        if user is None:
            # user = User(username=username, password=form.password.data)
            # user = User(username=username)
            user = User()
            user.username = username
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
        else:
            flash('The username has been registered')
            return redirect(url_for('register.html', form=form))
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['post', 'get'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('username or password invalid')
            return redirect('login')
        login_user(user)
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You logout!')
    return redirect(url_for('index'))


@app.route('/blogs/<username>', methods=['post', 'get'])
@app.route('/blogs/<username>/<int:page>', methods=['post', 'get'])
@login_required
def blogs(username, page=1):
    user = User.query.filter_by(username=username).first()
    form = PostForm()
    if user is None:
        flash('the username is not valid.')
        return redirect(url_for('index'))
    if form.validate_on_submit():
        # post = Post(form.title.data, form.body.data)
        post = Post()
        post.title = form.title.data
        post.body = form.body.data
        post.author_id = current_user.id
        post.timestamp = datetime.utcnow()
        form.title.data = None
        form.body.data = None
        db.session.add(post)
        db.session.commit()
    POSTS_PER_PAGE = app.config['POSTS_PER_PAGE']
    posts = user.posts.order_by(desc(Post.timestamp)).paginate(page, POSTS_PER_PAGE, False)
    return render_template('blogs.html', posts=posts, form=form, user=user)


@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    return render_template('profile.html', user=user)


@app.route('/edit_profile', methods=['post', 'get'])
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        current_user.sex = form.sex.data
        current_user.location = form.location.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('you edit your profile successful!')
        return redirect(url_for('user', username=current_user.username))
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@app.route('/followeds/<username>')
def followeds(username):
    # followeds = User.query.filter_by(username=username).first().followeds.order_by('timestamp')
    user = User.query.filter_by(username=username).first()
    users = {}
    if user is None:
        flash('the user is not registed')
    else:
        followeds = user.followed.order_by(desc(Follow.timestamp)).all()
        for follow in followeds:
            followed = User.query.get(follow.followed_id)
            users[followed.username] = follow.timestamp
    return render_template('followeds.html', users=users)


@app.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    users = {}
    if user is None:
        flash('the user is not registed')
    else:
        followers = user.followers.order_by(desc(Follow.timestamp)).all()
        for follow in followers:
            follower = User.query.get(follow.follower_id)
            users[follower.username] = follow.timestamp
    return render_template('followers.html', users=users)


@app.route('/post/<int:id>', methods=['get', 'post'])
def post(id):
    post = Post.query.get(id)
    if post is None:
        flash('the post_id is not valid')
        return redirect(url_for('index'))
    form = CommentForm()

    comments = post.comments.order_by(Comment.timestamp).all()

    if form.validate_on_submit():
        comment = Comment(body=form.body.data, author=current_user._get_current_object(),
                          post=post)
        # comment = Comment(body=form.body.data, author_id=current_user.id, post=post)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post', id=post.id))
    return render_template('blog.html', post=post, form=form, comments=comments)


@app.route('/delete_blog/<int:id>', methods=['get', 'post'])
def delete_blog(id):
    blog = Post.query.get(id)
    if blog is None:
        flash('the blog id is not valid!')
    else:
        db.session.delete(blog)
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/delete_comment/<int:id>', methods=['get', 'post'])
def delete_comment(id):
    comment = Comment.query.get(id)
    if comment is None:
        flash('the comment id id not valid!')
    else:
        db.session.delete(comment)
        db.session.commit()
    return redirect(url_for('blog', id=comment.post.id))


