from tracemalloc import start
import paho.mqtt.client as mqtt
import time
from chess import BLACK, WHITE

NAME = "chess"
LOBBY = f"{NAME}/lobby"
GAME = f"{NAME}/game"

QUIT = "quit"


class ChessMqttClient(mqtt.Client):

    def __init__(self, host, board):
        super().__init__()
        self.game_channel = None
        self.game_active = False
        self.game_started = False
        self.player = None
        self.opponent = None
        self.host = host
        self.board = board
    
    def start(self):
        
        self.loop_start()
        self.connect(self.host, 1883, 60)
        print("waiting for connection...")
        while not self.is_connected():
            time.sleep(0.1)

        if self.game_channel == None:
            self.game_channel = f"l-{time.time()}"
            self.player = WHITE
            self.opponent = BLACK
            
            print(f"Starting new game {self.game_channel}")
            self.unsubscribe(LOBBY)
            self.subscribe(f"{GAME}/{self.game_channel}/{self.opponent}")
            self.publish(LOBBY, self.game_channel, retain=True)


    def is_active(self):
        return self.game_active
    
    def is_waiting(self):
        return self.board.whose_turn() == self.opponent
    
    def opponent_has_quit(self):
        return self.game_started and not self.game_active
    
    def set_game_channel(self, channel):
        self.game_channel = channel
    
    def set_game_active(self, is_active):
        self.game_active = is_active
    
    def set_game_started(self, has_started):
        self.game_started = has_started
    
    def set_player(self, player):
        self.player = player
    
    def set_opponent(self, opponent):
        self.opponent = opponent
    
    def publish_move(self, start_pos, end_pos):
        move_text = f"m-{start_pos[0]} {start_pos[1]} {end_pos[0]} {end_pos[1]}"
        self.publish(f"{GAME}/{self.game_channel}/{self.player}", move_text)
    
    def publish_quit(self):
        if self.opponent_has_quit():
            self.unsubscribe(f"{GAME}/{self.game_channel}/{self.opponent}")
        elif self.game_active:
            message_inf = self.publish(f"{GAME}/{self.game_channel}/{self.player}", QUIT)
            message_inf.wait_for_publish() # Add wait for publish as threading can mean program ends for client thread publishes quit message
            self.unsubscribe(f"{GAME}/{self.game_channel}/{self.opponent}")
        else:
            message_inf = self.publish(f"{LOBBY}", f"cancelled: {self.game_channel}", retain= True)
            message_inf.wait_for_publish() # Add wait for publish as threading can mean program ends for client thread publishes quit message
            self.unsubscribe(f"{LOBBY}")
        self.set_game_active(False)
    
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        if self.game_channel is not None:
            self.subscribe(f"{GAME}/{self.game_channel}/{self.opponent}")
        else:
            self.subscribe(f"{LOBBY}")
    
    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        
        if msg.topic == LOBBY:
        
            if msg.payload.decode('UTF-8')[0:2] == 'l-':
                self.set_game_channel(msg.payload.decode('UTF-8'))
                self.set_player(BLACK)
                self.set_opponent(WHITE)
                self.set_game_active(True)
                self.set_game_started(True)

                print(f"Connecting to {self.game_channel}")

                self.unsubscribe(f"{LOBBY}")
                self.subscribe(f"{GAME}/{self.game_channel}/{self.opponent}")
                self.publish(LOBBY, f"joined: {self.game_channel}", retain= True)
                self.publish(f"{GAME}/{self.game_channel}/{self.player}", f"joined: {self.game_channel}")
        
        elif msg.topic == f"{GAME}/{self.game_channel}/{self.opponent}":
            
            if msg.payload.decode('UTF-8') == f"joined: {self.game_channel}":
                self.set_game_active(True)
                self.set_game_started(True)
                self.unsubscribe(f"{LOBBY}")
            elif msg.payload.decode('UTF-8')[0:2] == "m-":
                # Move message in form: m-1 2 3 4
                move_text = msg.payload.decode('UTF-8')[2:]
                coords_text = move_text.split()
                coords = [int(coord) for coord in coords_text]
                self.board.move_piece(*coords)
            elif msg.payload.decode('UTF-8') == QUIT:
                self.set_game_active(False)

        else:
            print(f"Unknown message: {msg.payload.decode('UTF-8')}")
