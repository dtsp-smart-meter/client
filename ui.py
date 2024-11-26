# Import necessary PyQt5 modules required for UI components and layouts.
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QFrame, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.Qt import QSizePolicy

# Import additional moduled required for functionality.
from datetime import datetime
from websocket_client import WebSocketClient
from data_provider import get_current_usage
from config import Config
import random
import json

class SmartMeter(QMainWindow):
    def __init__(self):
        super().__init__()

        # Random update interval between 15 and 60 seconds.
        self.update_interval_seconds = random.randint(15, 60)

        # Initialize the main window.
        self.setWindowTitle("Smart Meter")
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: #ecf0f1;")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.frame = QFrame()
        self.frame.setStyleSheet("background-color: #ffffff; border-radius: 10px; padding: 20px;")
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.frame)

        self.frame_layout = QVBoxLayout(self.frame)
        self.current_usage_layout = QHBoxLayout()
        self.current_cost_layout = QHBoxLayout()
        self.total_bill_layout = QHBoxLayout()

        self._create_labels()
        self._add_data_labels_to_layouts()
        self._create_status_section()
        self._set_label_styles()

        # WebSocket client setup and connections.
        self.websocket_client = WebSocketClient()
        self.websocket_client.connected_signal.connect(self.update_data)
        self.websocket_client.message_signal.connect(self.on_message)
        self.websocket_client.alert_signal.connect(self.show_alert)
        self.websocket_client.connect()

        # Timer to trigger data updates.
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(self.update_interval_seconds * 1000)

    def _create_labels(self):
        """Creates labels for current usage, cost, total bill, last update, and client ID."""

        self.current_usage_prefix = QLabel("Current Usage (kWh): ")
        self.current_usage_value = QLabel("0.00")
        self.current_cost_prefix = QLabel("Current Cost (£): ")
        self.current_cost_value = QLabel("0.00")
        self.total_bill_prefix = QLabel("Total Bill (£): ")
        self.total_bill_value = QLabel("0.00")
        self.last_update_label = QLabel(f"<b>Last Update:</b> <span style='color: #7f8c8d;'>Never</span>")
        self.client_id_label = QLabel(f"<b>Client ID:</b> <span style='color: #7f8c8d;'>{Config.CLIENT_ID}</span>")
        self.update_interval_label = QLabel(f"<b>Update Interval:</b> <span style='color: #7f8c8d;'>{self.update_interval_seconds} seconds</span>")

    def _add_data_labels_to_layouts(self):
        """Adds the created labels to the respective layouts."""

        current_usage_layout = QHBoxLayout()
        current_cost_layout = QHBoxLayout()
        total_bill_layout = QHBoxLayout()

        current_usage_layout.addWidget(self.current_usage_prefix)
        current_usage_layout.addWidget(self.current_usage_value)
        current_cost_layout.addWidget(self.current_cost_prefix)
        current_cost_layout.addWidget(self.current_cost_value)
        total_bill_layout.addWidget(self.total_bill_prefix)
        total_bill_layout.addWidget(self.total_bill_value)

        current_usage_wrapper = self._add_centered_layout(current_usage_layout)
        current_cost_wrapper = self._add_centered_layout(current_cost_layout)
        total_bill_wrapper = self._add_centered_layout(total_bill_layout)

        self.frame_layout.addLayout(current_usage_wrapper)
        self.frame_layout.addLayout(current_cost_wrapper)
        self.frame_layout.addLayout(total_bill_wrapper)

    def _add_centered_layout(self, layout):
        """Centers the provided layout in a wrapper."""

        wrapper = QHBoxLayout()
        wrapper.addLayout(layout)
        wrapper.setAlignment(Qt.AlignVCenter)

        return wrapper

    def _create_status_section(self):
        """Creates the status section for client ID, last update, and update interval."""

        self.status_widget = QWidget(self)
        self.status_layout = QVBoxLayout(self.status_widget)

        self.status_layout.addWidget(self.client_id_label)
        self.status_layout.addWidget(self.last_update_label)
        self.status_layout.addWidget(self.update_interval_label)

        self.layout.addWidget(self.status_widget, alignment = Qt.AlignBottom | Qt.AlignLeft)

    def _set_label_styles(self):
        """Sets the style for the labels."""

        for label in [self.current_usage_prefix, self.current_cost_prefix, self.total_bill_prefix]:
            label.setStyleSheet("color: #2c3e50; font-size: 16px; font-weight: bold; padding: 5px;")
            label.setAlignment(Qt.AlignLeft)

        for label in [self.current_usage_value, self.current_cost_value, self.total_bill_value]:
            label.setStyleSheet("color: #3498db; font-size: 16px; font-weight: bold; padding: 5px;")
            label.setAlignment(Qt.AlignRight)

        for label in [self.client_id_label, self.last_update_label, self.update_interval_label]:
            label.setStyleSheet("color: #7f8c8d; font-size: 12px;")

    def update_last_update_time(self, timestamp):
        """Updates the 'Last Update' label with the provided timestamp."""

        formatted_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.last_update_label.setText(f"<b>Last Update:</b> <span style='color: #7f8c8d;'>{formatted_time}</span>")

    def update_data(self):
        """Sends the current meter reading to the WebSocket server."""

        self.websocket_client.send_meter_reading(get_current_usage())

    def show_alert(self, message):
        """Displays an alert message in a popup window."""

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
        """Handles incoming WebSocket messages and updates the UI accordingly."""

        message_data = json.loads(message)

        # Update data labels if the message contains meter reading data.
        if all(key in message_data for key in ["currentUsage", "currentCost", "totalBill"]):
            self.current_usage_value.setText(f"{message_data['currentUsage']:.2f}")
            self.current_cost_value.setText(f"{message_data['currentCost']:.2f}")
            self.total_bill_value.setText(f"{message_data['totalBill']:.2f}")
            self.update_last_update_time(message_data["timestamp"])
        # Show an alert if the message is an alert.
        elif "message" in message_data:
            self.show_alert(message_data["message"])

    def closeEvent(self, event):
        """Handles the window close event and disconnects the WebSocket client."""
        
        self.websocket_client.disconnect()
        super().closeEvent(event)