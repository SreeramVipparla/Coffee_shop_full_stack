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
!! THIS WILL DROP ALL RECORDS AND START DB FROM SCRATCH
'''
db_drop_and_create_all()

# ROUTES
'''
Implement endpoint GET /drinks
it is a public endpoint
it contains only the drink.short() data representation
returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'], endpoint='get_drinks_short')
def get_drinks():
     
    try:
        drinks = Drink.query.all()
    except:
        abort(400)
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })

'''
Implement endpointGET /drinks-detail
it requires the 'get:drinks-detail' permission
it contains the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):

    drink_query = Drink.query.all()
    drinks = [drink.long() for drink in drink_query]

    if len(drinks) == 0:
        abort(404)

    try:
        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200

    except Exception as e:
        print('\n'+'Error modifying drinks-detail: ', e)
        abort(404)

'''
Implement endpoint POST /drinks
it creates a new row in the drinks table
it requires the 'post:drinks' permission
it contains the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(jwt):


    data = dict(request.form or request.json or request.data)
    try:
        title = data.get('title')
        if type(data.get('recipe')) == str:
            recipe = data.get('recipe')
        else:
            recipe = json.dumps(data.get('recipe'))
        
    except:
        abort(400)

    if title == '' or recipe == '':
        abort(400)

    drink = Drink(title=title, recipe=recipe)
    drink.insert()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })

'''
Implement endpoint PATCH /drinks/<id>
where <id> is the existing model id
it responds with a 404 error if <id> is not found
it updates the corresponding row for <id>
it requires the 'patch:drinks' permission
it contains the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):

    data = request.get_json()
    title = data.get('title', None)
    recipe = data.get('recipe')

    drink = Drink.query.filter_by(id=drink_id).one_or_none()

    if title is None:
        abort(400)


    if drink is None:
        abort(404)

    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except:
        abort(404)
'''
Implement endpointDELETE /drinks/<id>
where <id> is the existing model id
it responds with a 404 error if <id> is not found
it deletes the corresponding row for <id>
it requires the 'delete:drinks' permission
returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):

    try:
        drink=Drink.query.get(drink_id)
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200
    except:
        abort(404)


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
Implement error handlers using the @app.errorhandler(error) decorator
    each error handler returns (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''

@app.errorhandler(400)
def Bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400

'''
Implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def Not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404


'''
Implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code