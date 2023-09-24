import sys
import os
import warnings

from pyuac import main_requires_admin

from gui.main_window import Main_window


@main_requires_admin
def main():

    app = Main_window()
    app.mainloop()
    warnings.filterwarnings("ignore", category=UserWarning)


def run_as_admin():
    import ctypes

    ctypes.windll.shell32.ShellExecuteW(

        None, "runas", sys.executable, " ".join(sys.argv), None, 1)


if __name__ == "__main__":
    main()
