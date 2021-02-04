import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
def get_short_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]
    return formatted_drinks

def get_long_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]
    return formatted_drinks
    

@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = get_short_drinks()
    except:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': drinks
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth(permission='get:drinks-detail')
def drinks_detail(payload):
    try:
        drinks = get_long_drinks()
    except:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': drinks
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
#####################################################
@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def post_drink(payload):
    try:
        title = request.get_json()['title']
        recipe = request.get_json()['recipe']
        print(title)
        print(recipe)
    except:
        abort(400)
    
    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
    except:
        abort(422)
    
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })
#####################################################

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def edit_drink(payload, id):
    
    drink = Drink.query.filter(Drink.id==id).one_or_none()
    if not drink:
        abort(404)
    body = request.get_json()
    

    if 'title' in body:
        drink.title = body['title']
    if 'recipe' in body:
        drink.recipe = json.dumps(body['recipe'])

    try:
        drink.update()
    except:
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(payload, id):
  
    drink = Drink.query.filter(Drink.id==id).one_or_none()
    if not drink:
        abort(404)

    drink.delete()
    return jsonify({
        'success': True,
        'delete': id
    })

## Error Handling
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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    }), 400
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def authError(AuthError):
    return jsonify({
        "success": False, 
        "error": AuthError.status_code,
        "code": AuthError.error['code'],
        "description": AuthError.error['description']
        }), AuthError.status_code
