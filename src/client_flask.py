import requests

class ChessFlaskClient:

    def __init__(self, host, board):
        player_resp = requests.put(f"{host}/player/new")
        if player_resp.status_code == 404:
            raise ValueError("Server not found")
        elif player_resp.status_code != 200:
            raise ValueError("Server error")
        
        self.game_active = False
        self.game_started = False
        self.address = host
        self.player = player_resp.json()
        self.board = board
    
    def publish_move(self, start_pos, end_pos):
        requests.post(f"{self.address}/move", json= {
            'player': self.player,
            'move': [start_pos, end_pos]
        })
    
    def publish_quit(self):
        requests.delete(f"{self.address}/game/reset")

    def is_active(self):
        if self.board.whose_turn() != self.player:
            # To improve performance only updates when is other persons turn
            self.game_active = requests.get(f"{self.address}/game/active").json()
        if self.game_active:
            self.game_started = True
        return self.game_active
    
    def is_active_force_check(self):
        self.game_active = requests.get(f"{self.address}/game/active").json()
        if self.game_active:
            self.game_started = True
        return self.game_active
    
    def is_waiting(self):
        waiting = False
        if self.board.whose_turn() != self.player:
            most_recent_move = requests.get(f"{self.address}/move").json()
            if most_recent_move['player'] == self.player:
                waiting = True
            else:
                waiting = False
                start_pos, end_pos = most_recent_move['move'][0], most_recent_move['move'][1]
                self.board.move_piece(*start_pos, *end_pos)
        return waiting
    
    def opponent_has_quit(self):
        return self.game_started and not self.game_active




