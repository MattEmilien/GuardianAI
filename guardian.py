import sys
import os
from pyuac import main_requires_admin
from gui.main_window import AntivirusApp


@main_requires_admin
def main():
    app = AntivirusApp()
    app.mainloop()


def run_as_admin():
    import ctypes
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1)


if __name__ == "__main__":
    main()
