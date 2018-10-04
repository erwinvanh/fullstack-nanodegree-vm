"""
Project for Udacity Fullstack webdevelopment Week 3
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Restaurant, MenuItem

APP = Flask(__name__)
ENGINE = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = ENGINE

SESSIONFACTORY = sessionmaker(bind=ENGINE)
SESSION = scoped_session(SESSIONFACTORY)

@APP.before_request
def before_request():
    """
    For each request start a new SESSION
    """
    SESSION()

@APP.route('/JSON')
@APP.route('/restaurants/JSON')
def restaurants_json():
    """
    Return all restaurants in JSON Format
    """
    try:
        restaurant = SESSION.query(Restaurant).all()
        return jsonify(Restaurants=[i.serialize for i in restaurant])
    except exc.SQLAlchemyError:
        return jsonify({"error": {"code": 404, "message": "Error reading restaurants"}})

@APP.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurant_menu_json(restaurant_id):
    """
    Return all menu-items for one restaurant in JSON Format
    """
    try:
        items = SESSION.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
        return jsonify(MenuItems=[i.serialize for i in items])
    except exc.SQLAlchemyError:
        return jsonify({"error": {"code": 404, "message": "Error reading menu"}})

@APP.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurant_menu_item_json(restaurant_id, menu_id):
    """
    Return a single menu-item in JSON Format
    """
    try:
        selected_item = SESSION.query(MenuItem).filter_by(id=menu_id).one()
        return jsonify(MenuItem=selected_item.serialize)
    except exc.SQLAlchemyError:
        return jsonify({"error": {"code": 404, "message": "Menu-item not found"}})


@APP.route('/')
@APP.route('/restaurants/')
def show_restaurants():
    """
    Show list of all restaurants
    """
    restaurants = SESSION.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)

@APP.route('/restaurant/new/', methods=['GET', 'POST'])
def new_restaurant():
    """
    Add a new restaurant
    GET : Show page to enter information on new restaurant
    POST : Add restaurant to database
    """
    if request.method == 'POST':
        add_it = Restaurant(
            name=request.form['name'])
        SESSION.add(add_it)
        SESSION.commit()
        flash("new restaurant created!")
        return redirect(url_for('show_restaurants'))
    return render_template('newRestaurant.html')

@APP.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    """
    Edit a restaurant
    GET : Show page to update information on restaurant
    POST : Update restaurant in database
    """
    try:
        edit_it = SESSION.query(Restaurant).filter_by(id=restaurant_id).one()
        if request.method == 'POST':
            if request.form['name']:
                edit_it.name = request.form['name']
                SESSION.add(edit_it)
                SESSION.commit()
                flash("Restaurant updated!")
            return redirect(url_for('show_restaurants'))
        return render_template('editrestaurant.html', restaurant=edit_it)
    except exc.SQLAlchemyError:
        return redirect(url_for('error'))

@APP.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
    """
    Delete a restaurant
    GET : Show page to confirm delete
    POST : Delete restaurant from database
    """
    delete_it = SESSION.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        SESSION.delete(delete_it)
        SESSION.commit()
        flash("Restaurant deleted")
        return redirect(url_for('show_restaurants'))
    return render_template('deleterestaurant.html', restaurant=delete_it)

@APP.route('/restaurant/<int:restaurant_id>/')
@APP.route('/restaurant/<int:restaurant_id>/menu/')
def show_menu(restaurant_id):
    """
    Show the menu for a restaurant
    """
    restaurant = SESSION.query(Restaurant).filter_by(id=restaurant_id).one()
    items = SESSION.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)

@APP.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def new_menu_item(restaurant_id):
    """
    Add a menu-item for the restaurant
    GET : Show page to enter menu-information
    POST : Add menu to database
    """
    if request.method == 'POST':
        new_item = MenuItem(
            name=request.form['name'],
            restaurant_id=restaurant_id,
            description=request.form['description'],
            price=request.form['price'],
            course=request.form['course'])
        SESSION.add(new_item)
        SESSION.commit()
        flash("Menu-item added")
        return redirect(url_for('show_menu', restaurant_id=restaurant_id))
    return render_template('newmenuitem.html', restaurant_id=restaurant_id)

@APP.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_id):
    """
    Edit a menu-item for a restaurant
    GET : Show page to edit menu-Item
    POST : Store update in database
    """
    edit_it = SESSION.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edit_it.name = request.form['name']
            edit_it.description = request.form['description']
            edit_it.price = request.form['price']
            edit_it.course = request.form['course']
            SESSION.add(edit_it)
            SESSION.commit()
        flash("Menu-item updated")
        return redirect(url_for('show_menu', restaurant_id=restaurant_id))
    return render_template('editmenuitem.html', restaurant_id=restaurant_id,
                           menu_id=menu_id, item=edit_it)

@APP.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_id):
    """
    Delete a menu-item for a restaurant
    GET : Show confirmation page
    POST : Delete from database
    """
    delete_it = SESSION.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        SESSION.delete(delete_it)
        SESSION.commit()
        flash("Menu-item deleted")
        return redirect(url_for('show_menu', restaurant_id=restaurant_id))
    return render_template('deletemenuitem.html', restaurant_id=restaurant_id,
                           menu_id=menu_id, item=delete_it)

@APP.route('/error/')
def error():
    """
    Show error page
    """
    return render_template('error.html')

@APP.after_request
def close_session(response):
    """
    Close the session after request is handled
    and pass on the original response
    """
    SESSION.remove()
    return response

if __name__ == '__main__':
    APP.secret_key = 'super_secret_key'
    APP.debug = True
    APP.run(host='0.0.0.0', port=5000)
