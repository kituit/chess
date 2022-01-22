from json import dumps
from flask import Flask, request
from chess import WHITE, BLACK

most_recent_move = {'player': BLACK, 'move': [(1, 1), (2, 1)]}

APP = Flask(__name__)

def validPost(data):
    if list(data.keys()) != ['player', 'move']:
        raise ValueError("Invalid post: Wrong paramters")

    if data['player'] not in [WHITE, BLACK]:
        raise ValueError("Invalid post: Invalid player")
    
    if len(data['move']) != 2 or len(data['move'][0]) != 2 or len(data['move'][1]) != 2:
        raise ValueError("Invalid post: Move in wrong format")

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

if __name__ == '__main__':
    APP.run()