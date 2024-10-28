import sys
from PyQt5.QtWidgets import QApplication
from ui import SmartMeter

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = SmartMeter()
    main_window.show()

    sys.exit(app.exec_())