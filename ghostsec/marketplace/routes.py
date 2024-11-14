from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, jsonify
from flask_login import current_user, login_required
from ghostsec import db
from ghostsec.models import MarketplaceItem, Order, ItemReview, User
from ghostsec.marketplace.forms import ItemForm, OrderForm, ReviewForm
from ghostsec.utils import save_picture
from datetime import datetime
import stripe
import os

marketplace = Blueprint('marketplace', __name__)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@marketplace.route("/marketplace")
def home():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    sort = request.args.get('sort', 'newest')
    
    query = MarketplaceItem.query.filter_by(is_approved=True)
    
    if category:
        query = query.filter_by(category=category)
        
    if sort == 'price_low':
        query = query.order_by(MarketplaceItem.price.asc())
    elif sort == 'price_high':
        query = query.order_by(MarketplaceItem.price.desc())
    elif sort == 'rating':
        query = query.order_by(MarketplaceItem.rating.desc())
    else:  # newest
        query = query.order_by(MarketplaceItem.date_posted.desc())
    
    items = query.paginate(page=page, per_page=12)
    return render_template('marketplace/home.html', items=items)

@marketplace.route("/marketplace/item/new", methods=['GET', 'POST'])
@login_required
def new_item():
    form = ItemForm()
    if form.validate_on_submit():
        if form.image.data:
            picture_file = save_picture(form.image.data, 'item_pics')
        else:
            picture_file = 'default_item.jpg'
            
        item = MarketplaceItem(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            stock=form.stock.data,
            is_digital=form.is_digital.data,
            image_file=picture_file,
            seller=current_user
        )
        db.session.add(item)
        db.session.commit()
        flash('Your item has been listed for sale!', 'success')
        return redirect(url_for('marketplace.home'))
    return render_template('marketplace/create_item.html', form=form)

@marketplace.route("/marketplace/item/<int:item_id>")
def item(item_id):
    item = MarketplaceItem.query.get_or_404(item_id)
    reviews = ItemReview.query.filter_by(item_id=item_id).order_by(ItemReview.date_posted.desc()).all()
    return render_template('marketplace/item.html', item=item, reviews=reviews)

@marketplace.route("/marketplace/item/<int:item_id>/update", methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    item = MarketplaceItem.query.get_or_404(item_id)
    if item.seller != current_user:
        abort(403)
    form = ItemForm()
    if form.validate_on_submit():
        if form.image.data:
            picture_file = save_picture(form.image.data, 'item_pics')
            item.image_file = picture_file
        item.name = form.name.data
        item.description = form.description.data
        item.price = form.price.data
        item.category = form.category.data
        item.stock = form.stock.data
        item.is_digital = form.is_digital.data
        db.session.commit()
        flash('Your item has been updated!', 'success')
        return redirect(url_for('marketplace.item', item_id=item.id))
    elif request.method == 'GET':
        form.name.data = item.name
        form.description.data = item.description
        form.price.data = item.price
        form.category.data = item.category
        form.stock.data = item.stock
        form.is_digital.data = item.is_digital
    return render_template('marketplace/create_item.html', form=form, legend='Update Item')

@marketplace.route("/marketplace/item/<int:item_id>/delete", methods=['POST'])
@login_required
def delete_item(item_id):
    item = MarketplaceItem.query.get_or_404(item_id)
    if item.seller != current_user:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('Your item has been deleted!', 'success')
    return redirect(url_for('marketplace.home'))

@marketplace.route("/marketplace/item/<int:item_id>/purchase", methods=['GET', 'POST'])
@login_required
def purchase_item(item_id):
    item = MarketplaceItem.query.get_or_404(item_id)
    form = OrderForm()
    
    if form.validate_on_submit():
        try:
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(item.price * 100),  # Convert to cents
                currency='usd',
                metadata={'integration_check': 'accept_a_payment'}
            )
            
            order = Order(
                buyer=current_user,
                item=item,
                quantity=form.quantity.data,
                total_price=item.price * form.quantity.data,
                payment_method='card',
                transaction_id=intent.id
            )
            
            # Update stock
            item.stock -= form.quantity.data
            
            db.session.add(order)
            db.session.commit()
            
            flash('Purchase successful!', 'success')
            return redirect(url_for('marketplace.order_confirmation', order_id=order.id))
            
        except Exception as e:
            flash('An error occurred during purchase. Please try again.', 'danger')
            return redirect(url_for('marketplace.item', item_id=item_id))
            
    return render_template('marketplace/purchase.html', item=item, form=form)

@marketplace.route("/marketplace/order/<int:order_id>")
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.buyer != current_user:
        abort(403)
    return render_template('marketplace/order_confirmation.html', order=order)

@marketplace.route("/marketplace/orders")
@login_required
def orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(buyer=current_user)\
        .order_by(Order.date_ordered.desc())\
        .paginate(page=page, per_page=10)
    return render_template('marketplace/orders.html', orders=orders)

@marketplace.route("/marketplace/item/<int:item_id>/review", methods=['GET', 'POST'])
@login_required
def review_item(item_id):
    item = MarketplaceItem.query.get_or_404(item_id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        review = ItemReview(
            rating=form.rating.data,
            review=form.review.data,
            item=item,
            user_id=current_user.id
        )
        
        # Update item rating
        reviews = ItemReview.query.filter_by(item_id=item_id).all()
        total_rating = sum([r.rating for r in reviews]) + form.rating.data
        item.rating = total_rating / (len(reviews) + 1)
        
        db.session.add(review)
        db.session.commit()
        flash('Your review has been posted!', 'success')
        return redirect(url_for('marketplace.item', item_id=item_id))
        
    return render_template('marketplace/review.html', form=form, item=item)
