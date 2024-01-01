# ‼️ Deprecation note ‼️
This repository will no longer be maintained. Better use [Vanadium](https://modrinth.com/mod/vanadium) (1.20+) or [Colormatica](https://modrinth.com/mod/colormatic) (1.19 and lower) mod

# Colormaps fixer
Remakes Minecraft texture pack a little to remove usage of unsupported for Iris Shaders Optifine colormaps

## How to use?
Install executable from Releases tab, then just drag-n-drop resource pack to executable. You can also run it from command line / terminal like this:

```
path/to/CMFixer "other/path/to/texture/pack.zip"
```

## Building yourself
Basically, you don't need to, but if you want, you can follow these steps:
1. Install Python 3.11 (other versions not supported)
2. Copy this repository through Github or `git` command
```
git clone https://github.com/mrzenc/cmfixer.git
```
3. Install required modules
```
pip install -r requirements.txt
```
4. Run `setup.py`, which will build executable for you
```
python setup.py
```
