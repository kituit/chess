# Compiles program at dist/chess, run script bash compile_gui.sh
pyinstaller --add-data 'src/img/sprites.png:src/img' -F src/game.py -n chess
rm -r build