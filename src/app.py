# Server app used for Flask mode of game multiplayer
# To use, run python3 -m flask run --host=0.0.0.0 to start flask server, and then run 
# python3 src/gui.py --flask <flask ip address>

from crypt import methods
from werkzeug.exceptions import HTTPException
from json import dumps
from flask import Flask, request
from chess import WHITE, BLACK

game_data = {
    'most_recent_move': {'player': BLACK, 'move': []},
    'assigned_white': False,
    'assigned_black': False,
    'game_active': False
}


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
    return dumps(game_data['most_recent_move'])

@APP.route('/move', methods=['POST'])
def post_new_move():
    data = request.get_json()
    global game_data
    validPost(data)
    game_data['most_recent_move'] = data
    return {}

@APP.route('/player/new', methods=['PUT'])
def new_player():
    global game_data
    if not game_data['assigned_white']:
        game_data['assigned_white'] = True
        return dumps(WHITE)
    elif not game_data['assigned_black']:
        game_data['game_active'] = True
        game_data['assigned_black'] = True
        return dumps(BLACK)
    else:
        raise AccessError("Already two players playing")

@APP.route('/game/active', methods=['GET'])
def is_game_active():
    return dumps(game_data['game_active'])

@APP.route('/game/reset', methods=['DELETE'])
def clear_game():
    global game_data
    game_data = {
        'most_recent_move': {'player': BLACK, 'move': []},
        'assigned_white': False,
        'assigned_black': False,
        'game_active': False
    }
    return {}

if __name__ == '__main__':
    APP.run()
