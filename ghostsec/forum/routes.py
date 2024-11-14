from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from ghostsec import db, socketio
from ghostsec.models import ForumPost, ForumComment
from ghostsec.forum.forms import PostForm, CommentForm
from . import forum

@forum.route('/forum')
def forum_home():
    page = request.args.get('page', 1, type=int)
    posts = ForumPost.query.order_by(
        ForumPost.date_posted.desc()
    ).paginate(page=page, per_page=10)
    return render_template('forum/home.html', posts=posts)

@forum.route('/forum/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = ForumPost(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        
        # Emit new post to all connected clients
        socketio.emit('new_post', {
            'id': post.id,
            'title': post.title,
            'author': post.author.username,
            'category': post.category,
            'date': post.date_posted.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        flash('Your post has been created!', 'success')
        return redirect(url_for('forum.forum_home'))
    return render_template('forum/create_post.html', 
                         title='New Post',
                         form=form,
                         legend='New Post')

@forum.route('/forum/post/<int:post_id>')
def post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    comments = ForumComment.query.filter_by(post_id=post_id)\
        .order_by(ForumComment.date_posted.desc()).all()
    form = CommentForm()
    return render_template('forum/post.html',
                         title=post.title,
                         post=post,
                         comments=comments,
                         form=form)

@forum.route('/forum/post/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = ForumComment(
            content=form.content.data,
            post_id=post.id,
            author=current_user
        )
        db.session.add(comment)
        db.session.commit()
        
        # Emit new comment to all connected clients
        socketio.emit('new_comment', {
            'id': comment.id,
            'content': comment.content,
            'author': comment.author.username,
            'post_id': post.id,
            'date': comment.date_posted.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        flash('Your comment has been added!', 'success')
    return redirect(url_for('forum.post', post_id=post.id))

@forum.route('/forum/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('forum.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category
    return render_template('forum/create_post.html',
                         title='Update Post',
                         form=form,
                         legend='Update Post')

@forum.route('/forum/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('forum.forum_home'))
