from PyInstaller.__main__ import run

if __name__ == '__main__':
    options = [
        '--name=CMFixer',
        '--onefile',
        '--clean',
        '--noconfirm',
        # '--distpath=./build', This causes error >:(
        './main.py',
    ]
    run(options)
