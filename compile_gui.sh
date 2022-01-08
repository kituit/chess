# Compiles program at dist/gui, run script bash compile_gui.sh
pyinstaller --add-data 'src/img/sprites.png:src/img' -F src/gui.py -n chess --specpath ./spec
rm -r build