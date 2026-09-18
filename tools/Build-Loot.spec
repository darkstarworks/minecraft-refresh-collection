# PyInstaller spec for Build-Loot.exe
#
# Build it from the tools/ folder on a Windows machine with Python 3 installed:
#
#     pip install pyinstaller pyyaml
#     pyinstaller Build-Loot.spec
#
# The finished Build-Loot.exe lands in tools/dist/ - copy it to the collection
# root, next to README.md, because it looks for loot/ and src/ beside itself.

a = Analysis(
    ["build_loot.py"],
    pathex=["."],
    datas=[("items.json", ".")],
    hiddenimports=["build_pack", "convert_26_3", "yaml"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas,
    name="Build-Loot",
    console=True,
    onefile=True,
)
