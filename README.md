# Python Chess

Chess api written in Python, with gui created using pygame.

![GUI created with pygame](/src/img/sample_chess_interface2.png "Sample interface")

## Files

### 1. chess.py

Chess API. To use, create an instance of the provided Board class, which stores the current state of
the game. Each cell in board grid is either 

| Board Method                                     | Description                                                                                 |
|--------------------------------------------------|---------------------------------------------------------------------------------------------|
| get_piece(row, col)                              | Returns the piece object that is being stored in chess grid at position given by (row, col) |
| whose_turn()                                     | Returns whose turn it is (BLACK/WHITE)                                                      |
| move_piece(curr_row, curr_col, new_row, new_col) | Moves piece from (curr_row, curr_col) to (new_row, new_col)                                 |
| is_in_check(colour)                              | For a given player colour BLACK/WHITE, returns TRUE/FALSE if player is in check             |

### 2. text_game.py

Basic text interface used for testing. 

### 3. game.py

Code for GUI and logic for running game. 

### 4. app.py

Contains code for flask server that can be deployed to run multiplayer in flask mode.

### 5. client_flask.py

Code for client that interfaces between game code and flask server.

### 6. client_mqtt.py

Code for client that manages online games and interfaces between players via MQTT.


## Playing with GUI

File containing GUI is located at src/game.py. To use, need pygame installed.

    pip3 install pygame

Game can be played in 3 modes: default (optional default flag --default), multiplayer via Flask Server (--flask flag), multipler via MQTT (--mqtt flag).

## Local Play

To play locally, run the following

    python3 src/game.py

## Multiplayer

There are two multiplayer implementations: 1) Flask Server, 2) MQTT. Flask server must be deployed
before being used, and only allows one game at a time, while MQTT can be operated using any 
MQTT broker (e.g test.mosquitto.org) and allows for unlimited number of simultaneous games.

### Flask

Haven't tested this beyond a local network but roughly speaking do the following:

1. Install flask on server device:

        pip3 install flask

2. Run the following command to start the server:

        python3 -m flask run --host=0.0.0.0

3. Copy the address from the flask output in the form http://\<domain\>:\<port\>, and then run the following command from the project directory on the device looking to play chess:
    
        python3 src/game.py --flask http://<domain>:<port>

### MQTT

Second implementation of multiplayer uses MQTT instead of a Flask Server. This has several advantages over server implementation. Firstly, MQTT is singificantly faster protocol compared to HTTP, and thus reduces latency and removes some compromises in code design that were done to reduce HTTP bottlenecks. Furthermore, MQTT implementation can be run using any MQTT broker (including free public ones like test.mosquitto.org), rather than requiring a server to be deployed. This implementation also allows an unlimited amount of games to run simultaneously, rather than only a single game that is allowed by flask server. 

To use, do the following:

1. Install paho-mqtt:

        pip3 install paho-mqtt

2. Run the following:

        python3 src/game.py --mqtt <host, e.g test.mosquitto.org>



## Compiling into executable

If you want game to be compiled into a single executable, install pyintaller and then run the provided
script compile_gui.sh.

    pip3 install pyinstaller
    bash compile_gui.sh

An executable 'chess' will be located in folder dist.