# Compiles program at dist/gui, run script bash compile_gui.sh
pyinstaller --add-data 'img/sprites.png:img' -F gui.py