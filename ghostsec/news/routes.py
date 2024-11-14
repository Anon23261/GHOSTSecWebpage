from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, jsonify
from flask_login import current_user, login_required
from ghostsec import db
from ghostsec.models import NewsArticle, NewsComment, NewsTag, User
from ghostsec.news.forms import ArticleForm, CommentForm
from ghostsec.utils import save_picture
from datetime import datetime

news = Blueprint('news', __name__)

@news.route("/news")
def home():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    tag = request.args.get('tag', None)
    
    query = NewsArticle.query.filter_by(is_approved=True)
    
    if category:
        query = query.filter_by(category=category)
    if tag:
        tag_obj = NewsTag.query.filter_by(name=tag).first()
        if tag_obj:
            query = query.filter(NewsArticle.tags.contains(tag_obj))
    
    articles = query.order_by(NewsArticle.date_posted.desc())\
        .paginate(page=page, per_page=10)
    
    # Get featured articles for sidebar
    featured_articles = NewsArticle.query\
        .filter_by(is_approved=True, is_featured=True)\
        .order_by(NewsArticle.date_posted.desc())\
        .limit(5)
    
    # Get popular tags
    tags = NewsTag.query\
        .join(NewsTag.articles)\
        .group_by(NewsTag.id)\
        .order_by(db.func.count(NewsArticle.id).desc())\
        .limit(10)
    
    return render_template('news/home.html', 
                         articles=articles,
                         featured_articles=featured_articles,
                         tags=tags)

@news.route("/news/article/new", methods=['GET', 'POST'])
@login_required
def new_article():
    if not current_user.is_admin:
        abort(403)
    form = ArticleForm()
    if form.validate_on_submit():
        if form.image.data:
            picture_file = save_picture(form.image.data, 'article_pics')
        else:
            picture_file = 'default_news.jpg'
            
        article = NewsArticle(
            title=form.title.data,
            content=form.content.data,
            summary=form.summary.data,
            category=form.category.data,
            image_file=picture_file,
            author_id=current_user.id
        )
        
        # Handle tags
        tags = [tag.strip() for tag in form.tags.data.split(',')]
        for tag_name in tags:
            tag = NewsTag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = NewsTag(name=tag_name)
                db.session.add(tag)
            article.tags.append(tag)
        
        db.session.add(article)
        db.session.commit()
        flash('Your article has been created!', 'success')
        return redirect(url_for('news.article', article_id=article.id))
    return render_template('news/create_article.html', form=form)

@news.route("/news/article/<int:article_id>")
def article(article_id):
    article = NewsArticle.query.get_or_404(article_id)
    if not article.is_approved and not current_user.is_admin:
        abort(403)
    
    # Increment view count
    article.views += 1
    db.session.commit()
    
    # Get comments
    comments = NewsComment.query\
        .filter_by(article_id=article_id, parent_id=None)\
        .order_by(NewsComment.date_posted.desc())\
        .all()
    
    return render_template('news/article.html', article=article, comments=comments)

@news.route("/news/article/<int:article_id>/update", methods=['GET', 'POST'])
@login_required
def update_article(article_id):
    article = NewsArticle.query.get_or_404(article_id)
    if not current_user.is_admin:
        abort(403)
    form = ArticleForm()
    if form.validate_on_submit():
        if form.image.data:
            picture_file = save_picture(form.image.data, 'article_pics')
            article.image_file = picture_file
        article.title = form.title.data
        article.content = form.content.data
        article.summary = form.summary.data
        article.category = form.category.data
        
        # Update tags
        article.tags = []
        tags = [tag.strip() for tag in form.tags.data.split(',')]
        for tag_name in tags:
            tag = NewsTag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = NewsTag(name=tag_name)
                db.session.add(tag)
            article.tags.append(tag)
        
        db.session.commit()
        flash('Your article has been updated!', 'success')
        return redirect(url_for('news.article', article_id=article.id))
    elif request.method == 'GET':
        form.title.data = article.title
        form.content.data = article.content
        form.summary.data = article.summary
        form.category.data = article.category
        form.tags.data = ', '.join([tag.name for tag in article.tags])
    return render_template('news/create_article.html', form=form, legend='Update Article')

@news.route("/news/article/<int:article_id>/delete", methods=['POST'])
@login_required
def delete_article(article_id):
    article = NewsArticle.query.get_or_404(article_id)
    if not current_user.is_admin:
        abort(403)
    db.session.delete(article)
    db.session.commit()
    flash('Your article has been deleted!', 'success')
    return redirect(url_for('news.home'))

@news.route("/news/article/<int:article_id>/comment", methods=['POST'])
@login_required
def comment_article(article_id):
    article = NewsArticle.query.get_or_404(article_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = NewsComment(
            content=form.content.data,
            article=article,
            author=current_user,
            parent_id=form.parent_id.data if form.parent_id.data else None
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!', 'success')
    return redirect(url_for('news.article', article_id=article_id))

@news.route("/news/article/<int:article_id>/like", methods=['POST'])
@login_required
def like_article(article_id):
    article = NewsArticle.query.get_or_404(article_id)
    article.likes += 1
    db.session.commit()
    return jsonify({'likes': article.likes})
