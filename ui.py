from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QFrame, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.Qt import QSizePolicy
from datetime import datetime
from websocket_client import WebSocketClient
from data_provider import get_current_usage
from config import Config
import json

class SmartMeter(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create main Smart Meter window
        self.setWindowTitle("Smart Meter")
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(500, 300)
        self.setStyleSheet("background-color: #ecf0f1;")

        # Create central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create main frame
        self.frame = QFrame()
        self.frame.setStyleSheet("background-color: #ffffff; border-radius: 10px; padding: 20px;")
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.frame)

        # Create layout for the main frame content
        self.frame_layout = QVBoxLayout(self.frame)

        # Create separate layouts for each line
        self.current_usage_layout = QHBoxLayout()
        self.current_cost_layout = QHBoxLayout()
        self.total_bill_layout = QHBoxLayout()

        # Create labels for current usage, current cost, and total bill
        self.current_usage_prefix = QLabel("Current Usage (kWh): ")
        self.current_usage_value = QLabel("0.00")
        self.current_cost_prefix = QLabel("Current Cost (£): ")
        self.current_cost_value = QLabel("0.00")
        self.total_bill_prefix = QLabel("Total Bill (£): ")
        self.total_bill_value = QLabel("0.00")

        # Style the current usage, current cost, and total bill labels
        self.set_label_styles()

        # Add current usage, current cost, and total bill labels to respective layouts
        self.current_usage_layout.addWidget(self.current_usage_prefix)
        self.current_usage_layout.addWidget(self.current_usage_value)
        self.current_cost_layout.addWidget(self.current_cost_prefix)
        self.current_cost_layout.addWidget(self.current_cost_value)
        self.total_bill_layout.addWidget(self.total_bill_prefix)
        self.total_bill_layout.addWidget(self.total_bill_value)

        # Wrap each layout in another layout for centering
        self.current_usage_wrapper = QHBoxLayout()
        self.current_cost_wrapper = QHBoxLayout()
        self.total_bill_wrapper = QHBoxLayout()

        # Add layouts to wrappers
        self.current_usage_wrapper.addLayout(self.current_usage_layout)
        self.current_cost_wrapper.addLayout(self.current_cost_layout)
        self.total_bill_wrapper.addLayout(self.total_bill_layout)

        # Vertically align each wrapped layout
        self.current_usage_wrapper.setAlignment(Qt.AlignVCenter)
        self.current_cost_wrapper.setAlignment(Qt.AlignVCenter)
        self.total_bill_wrapper.setAlignment(Qt.AlignVCenter)

        # Add the centered wrappers to the main frame layout
        self.frame_layout.addLayout(self.current_usage_wrapper)
        self.frame_layout.addLayout(self.current_cost_wrapper)
        self.frame_layout.addLayout(self.total_bill_wrapper)

        # Create status label
        self.status_label = QLabel(f"Last Update: Never | Client ID: {Config.CLIENT_ID}", self)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 10px;")
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        
        self.layout.addWidget(self.status_label, alignment = Qt.AlignLeft | Qt.AlignBottom)

        # Initialize WebSocket client
        self.websocket_client = WebSocketClient()
        self.websocket_client.message_signal.connect(self.on_message)
        self.websocket_client.alert_signal.connect(self.show_alert)
        self.websocket_client.connect()

        # Start updating the data every 15 seconds
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(5000)

    def set_label_styles(self):
        for label in [self.current_usage_prefix, self.current_cost_prefix, self.total_bill_prefix]:
            label.setStyleSheet("color: #2c3e50; font-size: 16px; font-weight: bold; padding: 5px;")
            label.setAlignment(Qt.AlignLeft)

        for label in [self.current_usage_value, self.current_cost_value, self.total_bill_value]:
            label.setStyleSheet("color: #3498db; font-size: 16px; font-weight: bold; padding: 5px;")
            label.setAlignment(Qt.AlignRight)

    def update_data(self):
        self.websocket_client.send_meter_reading(get_current_usage())

    def show_alert(self, message):
        # Display a popup notification
        alert = QMessageBox(self)
        alert.setWindowTitle("Alert")
        alert.setText(message)
        alert.setIcon(QMessageBox.Warning)
        
        alert.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                font-size: 12px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        alert.exec_()

    def on_message(self, message):
        message = json.loads(message)

        if all(key in message for key in ["currentUsage", "currentCost", "totalBill"]):
            # Update current usage, current cost, and total bill labels
            self.current_usage_value.setText(f"{message['currentUsage']:.2f}")
            self.current_cost_value.setText(f"{message['currentCost']:.2f}")
            self.total_bill_value.setText(f"{message['totalBill']:.2f}")

            # Update status label
            self.status_label.setText(f"Last Update: {datetime.utcfromtimestamp(message['timestamp']).strftime('%Y-%m-%d %H:%M:%S')} | Client ID: {Config.CLIENT_ID}")
        elif "message" in message:
            # Display an alert popup notification
            self.show_alert(message["message"])

    def closeEvent(self, event):
        self.websocket_client.disconnect()
        super().closeEvent(event)