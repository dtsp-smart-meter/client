from PyQt5.QtWidgets import QApplication
from ui import SmartMeter
import logging
import sys

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level = logging.INFO, format = "%(asctime)s - %(levelname)s - %(message)s")

    app = QApplication(sys.argv)

    main_window = SmartMeter()
    main_window.show()

    sys.exit(app.exec_())