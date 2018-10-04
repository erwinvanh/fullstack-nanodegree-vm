"""
Project for Udacity Fullstack webdevelopment
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

@APP.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurant_menu_json(restaurant_id):
    """
    Return all restaurants in JSON Format
    """
    #restaurant = Session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = SESSION.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])
@APP.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurant_menu_item_json(menu_id):
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
@APP.route('/restaurants/<int:restaurant_id>/')
def restaurant_menu(restaurant_id=1):
    """
    Return list of all restaurants (HTML)
    If no value if provided, default value is id 1
    """
    restaurant = SESSION.query(Restaurant).filter_by(id=restaurant_id).one()
    items = SESSION.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)

@APP.route('/restaurant/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    """
    Show empty page to add new menu-item (GET) or
    Add menu-item to database (POST)
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
        flash("new menu item created!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    return render_template('newmenuitem.html', restaurant_id=restaurant_id)

# Task 2: Create route for editMenuItem function here
@APP.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    """
    Show page to edit menu-item (GET)
    Store changes in database (POST)
    """
    edited_item = SESSION.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edited_item.name = request.form['name']
        SESSION.add(edited_item)
        SESSION.commit()
        flash("Menu item updated!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id,
                               menu_id=menu_id, item=edited_item)

# Task 3: Create a route for deleteMenuItem function here
@APP.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    """
    Show page to confirm deletion of menu_item(GET)
    Delete item (POST)
    """
    delete_item = SESSION.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        SESSION.delete(delete_item)
        SESSION.commit()
        flash("menu item deleted!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

    return render_template('deletemenuitem.html', restaurant_id=restaurant_id,
                           menu_id=menu_id, item=delete_item)

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
