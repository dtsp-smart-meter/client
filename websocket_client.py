from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
import websocket
import time
import ssl
import json
import re

class WebSocketClient(QThread):
    message_received = pyqtSignal(str)
    alert_signal = pyqtSignal(str)

    def __init__(self, client_id, host = "localhost", port = 8080):
        super().__init__()
        self.client_id = client_id
        self.host = host
        self.port = port
        self.url = f"wss://{host}:{port}/ws"
        self.ws = None
        self.running = False
        self.reconnect_delay = 5

    def connect(self):
        self.running = True
        self.start()

    def run(self):
        while self.running:
            try:
                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_message = self.on_message,
                    on_open = self.on_open,
                    on_error = self.on_error,
                    on_close = self.on_close
                )

                print(f"Connecting to {self.url}")

                self.ws.run_forever(sslopt = {"cert_reqs": ssl.CERT_NONE})
            except Exception as error:
                print(f"Error in WebSocket connection: {error}")
                self.alert_signal.emit(f"WebSocket connection error: {error}")

            if self.running:
                print(f"Reconnecting in {self.reconnect_delay} seconds...")
                time.sleep(self.reconnect_delay)

    def on_open(self, ws):
        print("WebSocket connection opened")
        connect_frame = (
            "CONNECT\n"
            f"accept-version:1.1,1.0\n"
            f"host:{self.host}\n"
            "heart-beat:10000,10000\n\n\0"
        )
        ws.send(connect_frame)
        subscribe_frame = (
            f"SUBSCRIBE\nid:sub-0\ndestination:/notification/readingResult/{self.client_id}\n\n\0"
        )
        ws.send(subscribe_frame)
        print(f"Subscribed to /notification/readingResult/{self.client_id}")
        subscribe_frame = (
            f"SUBSCRIBE\nid:sub-1\ndestination:/notification/alert\n\n\0"
        )
        ws.send(subscribe_frame)
        print(f"Subscribed to /notification/alert")

    def on_message(self, ws, message):
        # Extract the JSON part from the message.
        match = re.search(r'\{.*\}', message) # Find the first JSON-like structure.
        if match:
            json_message = match.group(0)
            
            try:
                data = json.loads(json_message)
                data = json.dumps(data)
                
                self.message_received.emit(data)

                print(f"Received message: {data}")
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")
        self.alert_signal.emit(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"WebSocket closed with code: {close_status_code}, message: {close_msg}")
        self.alert_signal.emit(f"WebSocket closed with code: {close_status_code}, message: {close_msg}")

    def send_message(self, current_usage):
        if self.ws and self.ws.sock and self.ws.sock.connected:
            try:
                timestamp = datetime.now().timestamp()
                payload = {
                    "clientId": self.client_id,
                    "currentUsage": current_usage,
                    "timestamp": timestamp
                }
                message = json.dumps(payload)
                send_frame = (
                    f"SEND\ndestination:/app/meterReading\n\n{message}\n\0"
                )
                self.ws.send(send_frame)
                print(f"Sent message: {message}")
            except websocket.WebSocketConnectionClosedException:
                print("Error: Connection is closed. Cannot send message.")
        else:
            print("Cannot send message, WebSocket is not connected.")

    def disconnect(self):
        self.running = False
        if self.ws:
            self.ws.close()