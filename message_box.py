import ctypes
import subprocess
import sys
from datetime import datetime


class MessageBox:
    @classmethod
    def _show_message(cls, title: str, message: str, icon: str):
        try:
            match sys.platform:
                case 'win32':
                    ctypes.windll.user32.MessageBoxW(None, title, message, cls._parse_icon(sys.platform, icon))
                case 'darwin':
                    subprocess.call(["/usr/bin/osascript", "-e", f'display dialog "{message}" with icon '
                                                                 f'{cls._parse_icon(sys.platform, icon)}'])
                case 'linux':
                    subprocess.call(["/usr/bin/zenity", cls._parse_icon(sys.platform, icon), '--title', title,
                                     '--text', message])
        except subprocess.CalledProcessError:
            file = open("output.txt", "a+")
            file.write(f"[{datetime.now().strftime('%b %-d %Y, %H:%M:%S')}]\nError occurred when creating message box, "
                       f"so output was redirected into this file instead.\n\n{title} {message}\n\n")
            file.close()

    @classmethod
    def show_info(cls, title: str, message: str):
        cls._show_message(title, message, "info")

    @classmethod
    def show_warning(cls, title: str, message: str):
        cls._show_message(title, message, "warning")

    @classmethod
    def show_error(cls, title: str, message: str):
        cls._show_message(title, message, "error")

    @classmethod
    def _parse_icon(cls, platform, icon):
        icon_dict = {
            'win32': {
                'error': 0x00000010,
                'warning': 0x00000030,
                'info': 0x00000040
            },
            'darwin': {
                'error': 'stop',
                'warning': 'caution',
                'info': 'note'
            },
            'linux': {
                'error': '--error',
                'warning': '--warning',
                'info': '--info'
            }
        }
        if platform in icon_dict.keys():
            return icon_dict[platform][icon]
