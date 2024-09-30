from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QFrame
from PyQt5.QtCore import QTimer, Qt
from PyQt5.Qt import QSizePolicy
import sys
import random
import pandas

# Simulate historical data
historical_data = {
    "Time": pandas.date_range(start = "2024-09-17", periods = 20, freq = "H"),
    "Usage": [random.uniform(1, 5) for _ in range(20)]
}

def get_electricity_data():
    current_usage = random.uniform(0.5, 5.0) # Simulate current usage in kWh
    total_usage = random.uniform(200, 1000) # Simulate total usage so far
    total_bill = total_usage * 0.20 # Assuming £0.20 per kWh

    return current_usage, total_usage, total_bill

# Simulating the addition of new data to historical data
def get_historical_data():
    global historical_data

    new_usage = random.uniform(0.5, 5.0)
    new_time = pandas.Timestamp.now()
    
    historical_data["Time"] = historical_data["Time"].append(pandas.DatetimeIndex([new_time]))
    historical_data["Usage"].append(new_usage)
    
    return pandas.DataFrame(historical_data)

class SmartMeter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Meter")
        self.setGeometry(100, 100, 600, 400) # left, top, width, height
        self.setFixedSize(600, 400) # Stop the window from being resized
        self.setStyleSheet("background-color: #ecf0f1;")

        # Create the central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create the layout
        self.layout = QVBoxLayout(self.central_widget)

        # Create the main frame
        self.frame = QFrame()
        self.frame.setStyleSheet("background-color: #ffffff; border-radius: 10px; padding: 20px;")
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.frame)
        
        # Create the inner layout for the main frame
        self.frame_layout = QVBoxLayout(self.frame)

        # Create labels for displaying usage and bill information
        self.current_usage_label = QLabel("Current Usage (kWh): 0")
        self.current_cost_label = QLabel("Current Cost (£): 0")
        self.total_bill_label = QLabel("Total Bill (£): 0")

        # Set label styles
        self.set_label_styles([self.current_usage_label, self.current_cost_label, self.total_bill_label])

        # Add labels to frame layout
        self.frame_layout.addWidget(self.current_usage_label)
        self.frame_layout.addWidget(self.current_cost_label)
        self.frame_layout.addWidget(self.total_bill_label)

        # Create status label
        self.status_label = QLabel("", self)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 10px;")
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.layout.addWidget(self.status_label, alignment = Qt.AlignLeft | Qt.AlignBottom)

        # Start auto-refreshing the data every 15 seconds
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(15000) # 15 seconds interval

        # Initial refresh to load data on startup
        self.refresh_data()

    def set_label_styles(self, labels):
        for label in labels:
            label.setStyleSheet("color: #2c3e50; font-size: 16px; font-weight: bold; padding: 10px;")
            label.setAlignment(Qt.AlignCenter)

    def refresh_data(self):
        # Get new electricity usage data
        usage, total_usage, bill = get_electricity_data()

        # Update the labels
        self.current_usage_label.setText(f"Electricity Usage (kWh): {usage:.2f}")
        self.current_cost_label.setText(f"Current Cost (£): {usage * 0.15:.2f}")
        self.total_bill_label.setText(f"Total Bill (£): {bill:.2f}")

        current_time = pandas.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        client_id = "12345678" # Fake client ID

        # Update status label with last update time and client ID
        self.status_label.setText(f"Last Update: {current_time} | Client ID: {client_id}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = SmartMeter()
    main_window.show()

    sys.exit(app.exec_())