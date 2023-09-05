import sys
import os
from pyuac import main_requires_admin
from gui.main_window import MainWindow

@main_requires_admin
def main():
    # Check if the application is running with administrative privileges (Windows)
    # if os.name == 'nt' and not os.environ.get('APP_ADMIN'):
    #     # Relaunch the application with administrative privileges
    #     run_as_admin()
    #     sys.exit(0)

    # Initialize and start the GUI
    app = MainWindow()
    app.run()

def run_as_admin():
    import ctypes
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

if __name__ == "__main__":
    main()
