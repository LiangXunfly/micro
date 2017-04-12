# -*- coding: UTF-8 -*-
from flask import redirect, render_template, flash, url_for, current_app, request
from . import main
from .forms import PostForm, CommentForm, ProfileForm, EditPasswordForm, UploadForm,\
    ReplyForm, AlbumForm
from .forms import EditPersonalForm, PhotoForm
from ..models import User, Post, Follow, Comment, Praise, Collection, Message, Image, Report
from ..models import Album, Photo
from .. import db
from datetime import datetime
from flask_login import login_required, current_user
from sqlalchemy import desc, and_
from .. import photos
types = [Post, Praise, Collection, Comment, Follow, Report]


@main.route('/', methods=['post', 'get'])
@main.route('/index', methods=['post', 'get'])
@main.route('/index/<int:page>', methods=['POST', 'GET'])
def index(page=1):
    form = PostForm()
    posts = list()
    if current_user.is_authenticated:
        target = [current_user.id]
        for follow in current_user.followed.all():
            target.append(follow.followed_id)
        # all_posts = Post.query.filter(Post.author_id in target)
        all_posts = Post.query.filter(Post.author_id.in_(target))
        POSTS_PER_PAGE = current_app.config['POSTS_PER_PAGE']
        posts = all_posts.filter(Post.is_published==True).order_by(desc(Post.timestamp)).paginate(page, POSTS_PER_PAGE, False)
    if form.validate_on_submit():
        if current_user.is_invalid():
            flash('你当前权限受限，不能进行发表微博操作')
            return redirect(request.referrer)
        post = Post(title=form.title.data, body=form.body.data)
        form.title.data = ''
        form.body.data = ''
        post.author_id = current_user.id
        db.session.add(post)
        db.session.commit()
        if form.photo.data:
            filename = photos.save(form.photo.data)
            file_url = photos.url(filename)
            image = Image(url_path=file_url, post_id=post.id)
            db.session.add(image)
            db.session.commit()
        for follow in current_user.followers:
            message = Message(receive_id=follow.follower.id, refer_id=post.id, post_id=post.id, type=5)
            db.session.add(message)
        db.session.commit()
        flash('You post microblog "%s" just now' % post.title)
        return redirect(url_for('main.blogs', username=current_user.username))
    return render_template('main/index.html', form=form, posts=posts)


@main.route('/upload_avatar', methods=['GET', 'POST'])
def upload_avatar():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        current_user.avatar_url = file_url
        db.session.add(current_user._get_current_object())
        db.session.commit()
    else:
        file_url = None
    return render_template('main/upload_file.html', form=form, file_url=file_url)


@main.route('/blogs/<username>', methods=['post', 'get'])
@main.route('/blogs/<username>/<int:page>', methods=['post', 'get'])
@login_required
def blogs(username, page=1):
    user = User.query.filter_by(username=username).first()
    form = PostForm()
    if user is None:
        flash('the username is not valid.')
        return redirect(url_for('index'))
    if form.validate_on_submit():
        if current_user.is_invalid():
            flash('你当前权限受限，不能进行发表微博操作')
            return redirect(request.referrer)
        post = Post()
        post.title = form.title.data
        post.body = form.body.data
        post.author_id = current_user.id
        post.timestamp = datetime.now()
        form.title.data = None
        form.body.data = None
        db.session.add(post)
        db.session.commit()
        if form.photo.data:
            filename = photos.save(form.photo.data)
            file_url = photos.url(filename)
            image = Image(url_path=file_url, post_id=post.id)
            db.session.add(image)
            db.session.commit()
        for follow in current_user.followers:
            message = Message(receive_id=follow.follower.id, refer_id=post.id, post_id=post.id, type=5)
            db.session.add(message)
        db.session.commit()
        form.title.data = None
        form.body.data = None
    POSTS_PER_PAGE = current_app.config['POSTS_PER_PAGE']
    # posts = user.posts.order_by(desc(Post.timestamp)).paginate(page, POSTS_PER_PAGE, False)
    posts = user.posts.filter(Post.is_published==True).order_by(desc(Post.timestamp)).paginate(page, POSTS_PER_PAGE, False)
    return render_template('main/blogs.html', posts=posts, form=form, user=user)


@main.route('/personals')
@main.route('/personals/<int:page>')
@login_required
def personals(page=1):
    POSTS_PER_PAGE = current_app.config['POSTS_PER_PAGE']
    posts = current_user.posts.filter(Post.is_published==False).order_by(desc(Post.timestamp)).paginate(page, POSTS_PER_PAGE, False)
    return render_template('main/personals.html', posts=posts)


@main.route('/user/<username>')
@main.route('/user/<username>/<int:page>')
def user(username, page=1):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('此用户不存在')
        return redirect(request.referrer)
    return render_template('main/profile.html', user=user)


@main.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('the user is not valid')
        return redirect(request.referrer)
    if current_user.is_invalid():
        flash('你当前权限受限，不能进行关注操作')
        return redirect(request.referrer)
    current_user.follow(user)
    return redirect(url_for('main.user', username=user.username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('the user is not valid')
        return redirect(request.referrer)
    current_user.unfollow(user)
    return redirect(url_for('main.user', username=user.username))


@main.route('/followers/<username>')
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
    return render_template('main/followers.html', users=users, user=user)


@main.route('/followeds/<username>')
@login_required
def followeds(username):
    user = User.query.filter_by(username=username).first()
    users = {}
    if user is None:
        flash('the user is not registed')
    else:
        followeds = user.followed.order_by(desc(Follow.timestamp)).all()
        for follow in followeds:
            followed = User.query.get(follow.followed_id)
            users[followed.username] = follow.timestamp
    return render_template('main/followeds.html', users=users, user=user)


@main.route('/post/<int:id>', methods=['get', 'post'])
def post(id, message_id=None):
    post = Post.query.get(id)
    if post is None:
        flash('微博不存在')
        return redirect(url_for('main.index'))
    comments = post.comments.order_by(Comment.timestamp).all()
    return render_template('main/blog.html', post=post, comments=comments)


@main.route('/comment/<int:id>', methods=['GET', 'POST'])
@login_required
def comment(id):
    if current_user.is_invalid():
        flash('你当前权限受限，不能进行评论操作')
        return redirect(request.referrer)
    post = Post.query.get(id)
    if post is None:
        flash('the post_id is not valid')
        return redirect(url_for('main.index'))
    form = CommentForm()
    comments = post.comments.order_by(Comment.timestamp).all()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, author_id=current_user.id,
                          post_id=post.id)
        db.session.add(comment)
        post.score += 2
        db.session.add(post)
        db.session.commit()
        if current_user.id != post.author_id:
            message = Message(receive_id=post.author_id, refer_id=comment.id, post_id=post.id, type=3)
            db.session.add(message)
            db.session.commit()
        return redirect(url_for('main.post', id=post.id))
    return render_template('main/blog.html', post=post, form=form, comments=comments)


@main.route('/reply/<int:id>', methods=['get', 'post'])
@main.route('/reply/<int:id>/<int:message_id>', methods=['get', 'post'])
@login_required
def reply(id, message_id=None):
    comment = Comment.query.get(id)
    print(comment)
    if comment is None:
        flash('the comment_id is not valid')
        return redirect(url_for('main.post', id=comment.post_id))
    if message_id is not None:
        message = Message.query.get(message_id)
        message.readed = True
        db.session.add(message)
        db.session.commit()
    form = ReplyForm()
    if form.validate_on_submit():
        if current_user.is_invalid():
            flash('你当前权限受限，不能进行回复微博操作')
            return redirect(request.referrer)
        reply = Comment(body=form.body.data, post_id=comment.post_id, author_id=current_user.id,
                        replied_user_id=comment.author_id, comment_id=comment.id,
                        previous_comment_id=comment.id)
        db.session.add(reply)
        post = Post.query.get(comment.post_id)
        post.score += 2
        db.session.add(post)
        db.session.commit()
        comment.next_comment_id = reply.id
        db.session.add(comment)
        db.session.commit()
        message = Message(receive_id=comment.author_id, refer_id=reply.id, post_id=post.id, type=3)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('main.post', id=comment.post_id))

    comments = []

    # when some comment is deleted, error arise
    """
    while comment.comment_id is not None:
        comments.append(comment)
        comment = Comment.query.get(comment.comment_id)
    comments.append(comment)
    comments.reverse()
    """

    comments.append(comment)
    while comment.get_previous_comment() is not None:
        comments.append(comment.get_previous_comment())
        comment = comment.get_previous_comment()
    comments.reverse()
    return render_template('main/reply.html', comments=comments, form=form)


@main.route('/collect/<int:id>', methods=['get', 'post'])
def collect(id):
    post = Post.query.get(id)
    if post is None:
        flash('the post_id is not valid')
        return redirect(url_for('main.index'))
    current_user.collect(post)
    return redirect(request.referrer)


@main.route('/uncollect/<int:id>', methods=['get', 'post'])
def uncollect(id):
    post = Post.query.get(id)
    if post is None:
        flash('the post_id is not valid')
        return redirect(url_for('main.index'))
    current_user.uncollect(post)
    return redirect(request.referrer)


@main.route('/praise/<int:id>', methods=['get', 'post'])
def praise(id):
    post = Post.query.get(id)
    if post is None:
        flash('the post_id is not valid')
        return redirect(request.referrer)
    current_user.praise(post)
    return redirect(request.referrer)


@main.route('/report_post/<int:id>')
def report_post(id):
    post = Post.query.get(id)
    if post is None:
        flash('the post_id is not valid')
        return redirect(request.referrer)
    report = Report(author_id=current_user.id, refer_id=id, type=1)
    db.session.add(report)
    db.session.commit()
    flash("举报提交成功")
    return redirect(request.referrer)


@main.route('/report_comment/<int:id>')
def report_comment(id):
    comment = Comment.query.get(id)
    if comment is None:
        flash('the comment_id is not valid')
        return redirect(request.referrer)
    report = Report(author_id=current_user.id, refer_id=id, type=2)
    db.session.add(report)
    db.session.commit()
    flash("举报提交成功")
    return redirect(request.referrer)


@main.route('/unpraise/<int:id>', methods=['get', 'post'])
def unpraise(id):
    post = Post.query.get(id)
    if post is None:
        flash('the post_id is not valid')
        return redirect(url_for('main.index'))
    current_user.unpraise(post)
    return redirect(request.referrer)


@main.route('/get_praises_list/<int:id>')
def get_praise_list(id):
    post = Post.query.get(id)
    if post is None:
        flash('the post id is not valid')
        return redirect(url_for('main.index'))
    users = {}
    praises = post.praises.order_by(desc(Praise.timestamp)).all()
    for praise in praises:
        username = User.query.get(praise.author_id).username
        users[username] = praise.timestamp
    return render_template('main/get_praises_list.html', users=users)


@main.route('/praises')
@login_required
def praises():
    praises = current_user.praises.all()
    return render_template('main/praises.html', praises=praises)


@main.route('/delete_blog/<int:id>', methods=['get', 'post'])
def delete_blog(id):
    blog = Post.query.get(id)
    if blog is None:
        flash('the blog id is not valid!')
    else:
        if current_user.id != blog.author_id:
            flash('你不是该微博的作者，不能删除该微博')
            return redirect(url_for('main.post', id=blog.id))
        else:
            current_user.delete_post(blog)
            flash('成功删除一条微博')
            return redirect(url_for('main.blogs', username=current_user.username))
    return redirect(url_for('main.index'))


@main.route('/delete_comment/<int:id>', methods=['get', 'post'])
def delete_comment(id):
    comment = Comment.query.get(id)
    if comment is None:
        flash('the comment id id not valid!')
        return redirect(url_for('main.index'))
    else:
        if current_user.id != comment.author_id:
            flash('你不是该评论的作者，不能删除该评论')
            return redirect(url_for('main.post', id=comment.post_id))
        else:
            if comment.get_previous_comment() is None:
                next_comment = comment.get_next_comment()
                if next_comment:
                    next_comment.previous_comment_id = None
                    db.session.add(next_comment)
            elif comment.get_next_comment() is not None:
                next_comment = comment.get_next_comment()
                previous_comment = comment.get_previous_comment()
                next_comment.previous_comment_id = previous_comment.id
                db.session.add(next_comment)
            db.session.delete(comment)
            Message.query.filter(and_(Message.type == 3, Message.refer_id == comment.id)).delete()
            Report.query.filter(and_(Report.refer_id == comment.id, Report.type == 2)).delete()
            db.session.commit()
        return redirect(request.referrer)


@main.route('/edit_profile', methods=['post', 'get'])
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
    return render_template('main/edit_profile.html', form=form)


@main.route('/edit_password', methods=['GET', 'POST'])
def edit_password():
    form = EditPasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user._get_current_object())
            db.session.commit()
            return redirect(url_for('main.user', username=current_user.username))
        else:
            flash('you input the wrong password')
            return redirect(url_for('main.edit_password'))
    return render_template('main/edit_password.html', form=form)


@main.route('/get_collections')
@login_required
def get_collections():
    collections = current_user.collections.order_by(Collection.timestamp).all()
    target = []
    for collection in collections:
        target.append(collection.post_id)
    posts = Post.query.filter(Post.is_published==True).filter(Post.id.in_(target)).all()
    return render_template('main/collections.html', posts=posts)


@main.route('/make_personal/<int:id>')
@login_required
def make_personal(id):
    post = Post.query.get(id)
    if post is None:
        flash('this post id is not valid')
        return redirect(url_for('main.index'))
    post.is_published = False
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('main.personals'))


@main.route('/make_published/<int:id>')
@login_required
def make_published(id):
    post = Post.query.get(id)
    if post is None:
        flash('this post id is not valid')
        return redirect(url_for('main.index'))
    post.is_published = True
    db.session.add(post)
    db.session.commit()
    for follow in current_user.followers:
        message = Message(receive_id=follow.follower.id, refer_id=post.id, type=5)
        db.session.add(message)
    db.session.commit()
    return redirect(url_for('main.blogs', username=current_user.username))


@main.route('/edit_personal/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_personal(id):
    post = Post.query.get(id)
    if post is None:
        flash('this post id is not valid')
        return redirect(url_for('main.index'))
    form = EditPersonalForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        if form.post.data:
            post.is_published = True
            db.session.add(post)
            db.session.commit()
            for follow in current_user.followers:
                message = Message(receive_id=follow.follower.id, refer_id=post.id, type=5)
                db.session.add(message)
            db.session.commit()
            return redirect(url_for('main.blogs', username=current_user.username))
        elif form.save.data:
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('main.personals'))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('main/edit_personal.html', form=form)


@main.route('/messages')
@login_required
def messages():
    unreaded_messages = current_user.messages.filter(Message.readed == False).order_by(desc(Message.timestamp)).all()
    # readed_messages = current_user.messages.filter(Message.readed == True).order_by(desc(Message.timestamp)).all()
    # messages = unreaded_messages + readed_messages
    return render_template('main/unreaded_messages.html', messages=unreaded_messages, types=types)


@main.route('/see_message/<int:id>')
@login_required
def see_message(id):
    message = Message.query.get(id)
    if message.readed is not True:
        message.readed = True
        db.session.add(message)
        db.session.commit()
    elif message.type == 1:
        praise = Praise.query.get(message.refer_id)
        author = User.query.get(praise.author_id)
        post = Post.query.get(praise.post_id)
        return render_template('main/see_message.html', author=author, praise=praise, post=post, type=1)
    elif message.type == 2:
        collection = Collection.query.get(message.refer_id)
        author = User.query.get(collection.author_id)
        post = Post.query.get(collection.post_id)
        return render_template('main/see_message.html', author=author, collection=collection, post=post, type = 2)
    elif message.type == 3:
        comment = Comment.query.get(message.refer_id)
        author = User.query.get(comment.author_id)
        post = Post.query.get(comment.post_id)
        comments = [comment]
        while comment.get_previous_comment() is not None:
            comments.append(comment.get_previous_comment())
            comment = comment.get_previous_comment()
        comments.reverse()
        return render_template('main/see_message.html', author=author, comments=comments, post=post, type=3)
    elif message.type == 4:
        follow = Follow.query.get(message.refer_id)
        author = User.query.get(follow.follower_id)
        return render_template('main/see_message.html', author=author, follow=follow, type=4)
    elif message.type == 5:
        post = Post.query.get(message.refer_id)
        author = User.query.get(post.author_id)
        return render_template('main/see_message.html', author=author, post=post, type=5)
    elif message.type == 6:
        report = Report.query.get(message.refer_id)
        return render_template('main/see_message.html', report=report, type=6)


@main.route('/old_messages')
@login_required
def old_message():
    readed_messages = current_user.messages.filter(Message.readed == True).order_by(desc(Message.timestamp)).all()
    return render_template('main/readed_messages.html', messages=readed_messages, types=types)


@main.route('/same_city_friends')
@login_required
def same_city_friends():
    users = User.query.filter(User.location==current_user.location).filter(User.id!=current_user.id)
    return render_template('main/same_city_friends.html', users=users.all())


@main.route('/albums/<int:id>', methods=['GET', 'POST'])
@login_required
def albums(id):
    user = User.query.get(id)
    if user is None:
        flash('the user id is not valid')
        return redirect(request.referrer)
    form = AlbumForm()
    if form.validate_on_submit():
        name = form.name.data
        if Album.query.filter(Album.name == name).count() != 0:
            form.name.data = None
            flash('相册名已存在，请核对后再创建')
            return redirect(request.referrer)
        album = Album(author_id=current_user.id, name=form.name.data)
        db.session.add(album)
        db.session.commit()
        form.name.data = None
        form.submit.data = None
    albums = user.albums.all()
    return render_template('main/albums.html', user=user, albums=albums, form=form)


@main.route('/see_album/<int:id>', methods=['GET', 'POST'])
@login_required
def see_album(id):
    album = Album.query.get(id)
    if album is None:
        flash('the album id is not valid')
        return redirect(request.referrer)
    form = PhotoForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        photo = Photo(url_path=file_url, album_id=album.id, name=form.name.data)
        db.session.add(photo)
        db.session.commit()
        form.photo.data = None
        form.name.data = None
        return render_template('main/see_album.html', form=form, album=album)
    return render_template('main/see_album.html', form=form, album=album)


@main.route('/delete_photo/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_photo(id):
    photo = Photo.query.get(id)
    if photo is None:
        flash('the album id is not valid')
        return redirect(request.referrer)
    id = photo.album.id
    db.session.delete(photo)
    db.session.commit()
    return redirect(url_for('main.see_album', id=id))


@main.route('/test')
def test():
    return render_template('main/test.html', user=User.query.filter_by(username='LiangXunfly'))


@main.route('/user_search')
def user_search():
    pass
