from crypt import methods
from werkzeug.exceptions import HTTPException
from json import dumps
from flask import Flask, request
from chess import WHITE, BLACK

most_recent_move = {'player': BLACK, 'move': []}
assigned_white = False
assigned_black = False
game_active = False


def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

class InputError(HTTPException):
    code = 400
    message = 'No message specified'

class AccessError(HTTPException):
    code = 403
    message = 'No message specified'




APP = Flask(__name__)
APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)




def validPost(data):
    if list(data.keys()) != ['player', 'move']:
        raise InputError("Invalid post: Wrong paramters")

    if data['player'] not in [WHITE, BLACK]:
        raise InputError("Invalid post: Invalid player")
    
    if len(data['move']) != 2 or len(data['move'][0]) != 2 or len(data['move'][1]) != 2:
        raise InputError("Invalid post: Move in wrong format")

@APP.route('/move', methods=['GET'])
def get_most_recent():
    return dumps(most_recent_move)

@APP.route('/move', methods=['POST'])
def post_new_move():
    data = request.get_json()
    global most_recent_move
    validPost(data)
    most_recent_move = data
    return {}

@APP.route('/player/new', methods=['PUT'])
def new_player():
    global assigned_white
    global assigned_black
    if not assigned_white:
        assigned_white = True
        return dumps(WHITE)
    elif not assigned_black:
        global game_active
        game_active = True
        assigned_black = True
        return dumps(BLACK)
    else:
        raise AccessError("Already two players playing")

@APP.route('/game/active', methods=['GET'])
def is_game_active():
    return dumps(game_active)

@APP.route('/game/reset', methods=['DELETE'])
def clear_game():
    global assigned_white, assigned_black, game_active, most_recent_move
    most_recent_move = {'player': BLACK, 'move': []}
    assigned_white = False
    assigned_black = False
    game_active = False
    return {}

if __name__ == '__main__':
    APP.run()