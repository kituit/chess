# Compiles program at dist/gui, run script bash compile_gui.sh
pyinstaller --add-data 'src/img/sprites.png:img' -F src/gui.py
rm gui.spec