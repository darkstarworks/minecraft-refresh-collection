# Rebuilding Build-Loot.exe

`Build-Loot.exe` is the double-click version of `build_loot.py`. It has to be
built on Windows - PyInstaller cannot make a Windows program from Linux.

1. Copy the `tools` folder onto a Windows machine with Python 3 installed.
2. Open a command prompt in that folder and run:

       pip install pyinstaller pyyaml
       pyinstaller Build-Loot.spec

3. Take `dist\Build-Loot.exe` and drop it in the collection root, next to
   `README.md`. It has to sit there, because it looks for the `loot` and `src`
   folders beside itself.

Nothing else needs copying - `items.json` is baked into the program.

On Linux or Mac there is no exe: run `python3 tools/build_loot.py` instead.
