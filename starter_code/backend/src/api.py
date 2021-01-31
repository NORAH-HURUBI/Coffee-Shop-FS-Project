import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES
# GET /drinks
# it should be a public endpoint
# it contain only the drink.short() data representation.


@app.route('/drinks')
def get_drinks():
    try:
        drink = Drink.query.all()
        drinks_form = [drinks.short() for drinks in drink]

        return jsonify({
                       'success': True,
                       'drinks': drinks_form
                       }), 200
    except BaseException:
        abort(404)

# GET /drinks-detail
# it require the 'get:drinks-detail' permission.
# it contain the drink.long() data representation.


@app.route('/drinks-detail')
# only authorized users can perform this get.
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drink = Drink.query.all()
        drinks_form = [drinks.long() for drinks in drink]

        return jsonify({
                       'success': True,
                       'drinks': drinks_form
                       }), 200
    except BaseException:
        abort(404)


# POST /drinks..
# it create a new row in the drinks table
# it require the 'post:drinks' permission
# it contain the drink.long() data representation

@app.route('/drinks', methods=['POST'])
# only authorized users can perform this post.
@requires_auth('post:drinks')
def create_drink(payload):
    drink = request.get_json()
    new_title = drink['title']
    new_recipe = json.dumps(drink['recipe'])
    if new_title is None:
        abort(422)
    try:
        new_drink = Drink(title=new_title, recipe=new_recipe)
        new_drink.insert()
        drink_form = new_drink.long()

        return jsonify({
                       'success': True,
                       'drinks': drink_form
                       }), 200
    except BaseException:
        abort(400)

# PATCH /drinks/<id>
# where <id> is the existing model id
# it respond with a 404 error if <id> is not found
# it update the corresponding row for <id>
# it require the 'patch:drinks' permission
# it contain the drink.long() data representation

@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
# only authorized users can perform this patch.
def update_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        body = request.get_json()
        update_title = body.get('title')
        update_recipe = body.get('recipe')
        if drink is None:
            abort(404)

        if update_title is not None:
            drink.title = update_title

        if update_recipe is not None:
            drink.recipe = json.dumps(update_recipe)

        drink.update()
        drink_form = [drink.long()]
        return jsonify({
                       'success': True,
                       'drinks': drink_form,
                       }), 200

    except BaseException:
        abort(422)

# DELETE /drinks/<id>
# where <id> is the existing model id
# it should respond with a 404 error if <id> is not found
# it should delete the corresponding row for <id>
# it should require the 'delete:drinks' permission

@app.route('/drinks/<id>', methods=['DELETE'])
# only authorized users can perform this delete.
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
                       'success': True,
                       'delete': id,
                       }), 200

    except BaseException:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404


@app.errorhandler(400)
def badRequest(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                   "success": False,
                   "error": 401,
                   "message": 'Unathorized Request'
                   }), 401
