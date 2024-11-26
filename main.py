from PyQt5.QtWidgets import QApplication
from ui import SmartMeter
import logging
import sys

if __name__ == "__main__":
    # Configure the logging system for the application:
    # - Set the logging level to INFO (to log informational messages and above).
    # - Define the logging message format to include timestamp, log level, and the message.
    logging.basicConfig(level = logging.INFO, format = "%(asctime)s - %(levelname)s - %(message)s")

    # Create an instance of the QApplication, passing in the system's command-line arguments.
    # This initializes the application and provides access to global settings and resources.
    app = QApplication(sys.argv)

    # Create and displays an instance of the main window, represented by the SmartMeter class.
    main_window = SmartMeter()
    main_window.show()

    # Enter the application's event loop. This loop listens for and processes user interactions.
    # The program exits when the event loop ends (e.g. when the main window is closed).
    sys.exit(app.exec_())