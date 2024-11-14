"""Routes for social features."""
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, abort
from flask_login import login_required, current_user
from app import db, limiter
from models import (
    User, ForumCategory, ForumPost, ForumComment,
    Project, ProjectMember, ChatRoom, ChatMessage, ChatMember
)
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from schemas import PostSchema, CommentSchema

bp = Blueprint('social', __name__)

# Rate limiting decorators
post_limit = limiter.limit("5 per minute")
like_limit = limiter.limit("10 per minute")
comment_limit = limiter.limit("3 per minute")

# Forum routes
@bp.route('/forum')
def forum():
    """Display forum categories."""
    try:
        categories = ForumCategory.query.all()
        return render_template('forum/index.html', categories=categories)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error loading forum categories.', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/forum/category/<int:category_id>')
def forum_category(category_id):
    """Display posts in a category."""
    try:
        category = ForumCategory.query.get_or_404(category_id)
        posts = ForumPost.query.filter_by(category_id=category_id).order_by(
            ForumPost.is_pinned.desc(),
            ForumPost.date_posted.desc()
        ).all()
        return render_template('forum/category.html', category=category, posts=posts)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error loading category posts.', 'danger')
        return redirect(url_for('social.forum'))

@bp.route('/forum/post/new', methods=['GET', 'POST'])
@login_required
@post_limit
def new_post():
    """Create new forum post."""
    if request.method == 'POST':
        try:
            # Validate input
            post_schema = PostSchema()
            data = post_schema.load(request.form)
            
            post = ForumPost(
                title=data['title'],
                content=data['content'],
                author_id=current_user.id,
                category_id=data['category_id'],
                use_markdown=data.get('use_markdown', False)
            )
            db.session.add(post)
            db.session.commit()
            
            flash('Post created successfully!', 'success')
            return redirect(url_for('social.view_post', post_id=post.id))
        except ValidationError as e:
            flash('Invalid input data: ' + str(e.messages), 'danger')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error creating post.', 'danger')
    
    categories = ForumCategory.query.all()
    return render_template('forum/new_post.html', categories=categories)

@bp.route('/forum/post/<int:post_id>')
def view_post(post_id):
    """View forum post and comments."""
    try:
        post = ForumPost.query.get_or_404(post_id)
        post.views += 1
        db.session.commit()
        return render_template('forum/post.html', post=post)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error loading post.', 'danger')
        return redirect(url_for('social.forum'))

# Project routes with enhanced security
@bp.route('/projects')
def projects():
    """List public projects."""
    try:
        projects = Project.query.filter_by(is_public=True).all()
        return render_template('projects/index.html', projects=projects)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error loading projects.', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
@post_limit
def new_project():
    """Create new project."""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            repository_url = request.form.get('repository_url')
            is_public = request.form.get('is_public', type=bool)
            
            # Basic validation
            if not name or not description:
                flash('Name and description are required.', 'danger')
                return redirect(url_for('social.new_project'))
            
            project = Project(
                name=name,
                description=description,
                repository_url=repository_url,
                is_public=is_public,
                owner_id=current_user.id
            )
            db.session.add(project)
            db.session.commit()
            
            flash('Project created successfully!', 'success')
            return redirect(url_for('social.view_project', project_id=project.id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error creating project.', 'danger')
    
    return render_template('projects/new_project.html')

@bp.route('/projects/<int:project_id>')
def view_project(project_id):
    """View project details."""
    try:
        project = Project.query.get_or_404(project_id)
        if not project.is_public and project.owner_id != current_user.id:
            abort(403)
        return render_template('projects/project.html', project=project)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error loading project.', 'danger')
        return redirect(url_for('social.projects'))

# Chat routes with WebSocket support
@bp.route('/chat')
@login_required
def chat():
    """Display chat interface."""
    try:
        rooms = ChatRoom.query.filter(
            (ChatRoom.is_private == False) |
            (ChatRoom.members.any(user_id=current_user.id))
        ).all()
        return render_template('chat/index.html', rooms=rooms)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error loading chat rooms.', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/chat/room/<int:room_id>')
@login_required
def chat_room(room_id):
    """Display chat room."""
    try:
        room = ChatRoom.query.get_or_404(room_id)
        if room.is_private:
            member = ChatMember.query.filter_by(
                room_id=room_id,
                user_id=current_user.id
            ).first()
            if not member:
                abort(403)
        
        messages = ChatMessage.query.filter_by(room_id=room_id).order_by(
            ChatMessage.timestamp.asc()
        ).limit(100).all()  # Limit to last 100 messages for performance
        return render_template('chat/room.html', room=room, messages=messages)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error loading chat room.', 'danger')
        return redirect(url_for('social.chat'))

@bp.route('/chat/room/new', methods=['GET', 'POST'])
@login_required
@post_limit
def new_chat_room():
    """Create new chat room."""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            is_private = request.form.get('is_private', type=bool)
            
            if not name:
                flash('Room name is required.', 'danger')
                return redirect(url_for('social.new_chat_room'))
            
            room = ChatRoom(name=name, is_private=is_private)
            db.session.add(room)
            db.session.commit()
            
            # Add creator as admin member
            member = ChatMember(
                room_id=room.id,
                user_id=current_user.id,
                is_admin=True
            )
            db.session.add(member)
            db.session.commit()
            
            flash('Chat room created successfully!', 'success')
            return redirect(url_for('social.chat_room', room_id=room.id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error creating chat room.', 'danger')
    
    return render_template('chat/new_room.html')

# Video call routes with WebRTC
@bp.route('/call/<int:room_id>')
@login_required
def video_call(room_id):
    """Video call interface."""
    try:
        room = ChatRoom.query.get_or_404(room_id)
        if room.is_private:
            member = ChatMember.query.filter_by(
                room_id=room_id,
                user_id=current_user.id
            ).first()
            if not member:
                abort(403)
        
        return render_template('chat/video_call.html', room=room)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error accessing video call.', 'danger')
        return redirect(url_for('social.chat'))

# API routes with rate limiting
@bp.route('/api/post/<int:post_id>/like', methods=['POST'])
@login_required
@like_limit
def like_post(post_id):
    """Like/unlike a post."""
    try:
        post = ForumPost.query.get_or_404(post_id)
        post.likes += 1
        db.session.commit()
        return jsonify({'likes': post.likes})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to like post'}), 500

@bp.route('/api/comment/<int:comment_id>/like', methods=['POST'])
@login_required
@like_limit
def like_comment(comment_id):
    """Like/unlike a comment."""
    try:
        comment = ForumComment.query.get_or_404(comment_id)
        comment.likes += 1
        db.session.commit()
        return jsonify({'likes': comment.likes})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to like comment'}), 500

# Error handlers
@bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@bp.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
