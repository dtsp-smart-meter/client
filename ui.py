from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QFrame
from PyQt5.QtCore import QTimer, Qt
from PyQt5.Qt import QSizePolicy
from datetime import datetime
import json
import uuid
from websocket_client import WebSocketClient
from data_provider import get_electricity_data

class SmartMeter(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create random client ID.
        self.client_id = str(uuid.uuid4())

        # Create main Smart Meter window.
        self.setWindowTitle("Smart Meter")
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: #ecf0f1;")

        # Create central widget.
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create main frame.
        self.frame = QFrame()
        self.frame.setStyleSheet("background-color: #ffffff; border-radius: 10px; padding: 20px;")
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.frame)

        # Create layout for the main frame content.
        self.frame_layout = QVBoxLayout(self.frame)

        # Create separate layouts for each line.
        self.current_usage_layout = QHBoxLayout()
        self.current_cost_layout = QHBoxLayout()
        self.total_bill_layout = QHBoxLayout()

        # Create labels for current usage, current cost, and total bill.
        self.current_usage_prefix = QLabel("Current Usage (kWh): ")
        self.current_usage_value = QLabel("0.00")
        self.current_cost_prefix = QLabel("Current Cost (£): ")
        self.current_cost_value = QLabel("0.00")
        self.total_bill_prefix = QLabel("Total Bill (£): ")
        self.total_bill_value = QLabel("0.00")

        # Style the current usage, current cost, and total bill labels.
        self.set_label_styles()

        # Add current usage, current cost, and total bill labels to respective layouts.
        self.current_usage_layout.addWidget(self.current_usage_prefix)
        self.current_usage_layout.addWidget(self.current_usage_value)
        self.current_cost_layout.addWidget(self.current_cost_prefix)
        self.current_cost_layout.addWidget(self.current_cost_value)
        self.total_bill_layout.addWidget(self.total_bill_prefix)
        self.total_bill_layout.addWidget(self.total_bill_value)

        # Wrap each layout in another layout for centering.
        self.current_usage_wrapper = QHBoxLayout()
        self.current_cost_wrapper = QHBoxLayout()
        self.total_bill_wrapper = QHBoxLayout()

        # Add layouts to wrappers.
        self.current_usage_wrapper.addLayout(self.current_usage_layout)
        self.current_cost_wrapper.addLayout(self.current_cost_layout)
        self.total_bill_wrapper.addLayout(self.total_bill_layout)

        # Vertically align each wrapped layout.
        self.current_usage_wrapper.setAlignment(Qt.AlignVCenter)
        self.current_cost_wrapper.setAlignment(Qt.AlignVCenter)
        self.total_bill_wrapper.setAlignment(Qt.AlignVCenter)

        # Add the centered wrappers to the main frame layout.
        self.frame_layout.addLayout(self.current_usage_wrapper)
        self.frame_layout.addLayout(self.current_cost_wrapper)
        self.frame_layout.addLayout(self.total_bill_wrapper)

        # Create status label.
        self.status_label = QLabel(f"Last Update: Never | Client ID: {self.client_id}", self)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 10px;")
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        
        self.layout.addWidget(self.status_label, alignment = Qt.AlignLeft | Qt.AlignBottom)

        # Start updating the data every 15 seconds.
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(15000)

        # Initialize WebSocket client.
        self.websocket_client = WebSocketClient(client_id = self.client_id)
        self.websocket_client.message_received.connect(self.update_labels)
        self.websocket_client.connect()

        # Initial refresh to load data on startup.
        self.update_data()

    def set_label_styles(self):
        for label in [self.current_usage_prefix, self.current_cost_prefix, self.total_bill_prefix]:
            label.setStyleSheet("color: #2c3e50; font-size: 16px; font-weight: bold; padding: 5px;")
            label.setAlignment(Qt.AlignLeft)

        for label in [self.current_usage_value, self.current_cost_value, self.total_bill_value]:
            label.setStyleSheet("color: #3498db; font-size: 16px; font-weight: bold; padding: 5px;")
            label.setAlignment(Qt.AlignRight)

    def update_data(self):
        usage, total_usage, bill = get_electricity_data()
        self.websocket_client.send_message(usage)

    def update_labels(self, message):
        message = json.loads(message)

        # Update current usage, current cost, and total bill labels.
        self.current_usage_value.setText(f"{message['currentUsage']:.2f}")
        self.current_cost_value.setText(f"{message['cost']:.2f}")
        self.total_bill_value.setText(f"0.00")

        # Update status label.
        self.status_label.setText(f"Last Update: {datetime.utcfromtimestamp(message['timestamp']).strftime('%Y-%m-%d %H:%M:%S')} | Client ID: {self.client_id}")

    def closeEvent(self, event):
        self.websocket_client.disconnect()
        super().closeEvent(event)