from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
from config import Config
import websocket
import logging
import time
import json
import ssl
import re

class WebSocketClient(QThread):
    """
    WebSocketClient class to manage a WebSocket connection that communicates with the server.
    """
    
    # Define PyQt signals to communicate with the main UI thread
    message_signal = pyqtSignal(str)
    alert_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.websocket = None
        self.running = False
        self.reconnect_delay = 5 # Delay before reconnecting in case of WebSocket failure

    def connect(self):
        """
        Starts the WebSocket connection by setting the running flag to True and initiating the main thread.
        """
        self.running = True
        self.start()

    def run(self):
        """
        Main thread loop: attempts to connect to the WebSocket and reconnects automatically if the connection is lost.
        """
        while self.running:
            try:
                # Initialize and configure the WebSocket
                self.websocket = websocket.WebSocketApp(
                    Config.WEBSOCKET_URL,
                    on_open = self.on_open,
                    on_message = self.on_message,
                    on_error = self.on_error,
                    on_close = self.on_close
                )
                self.websocket.run_forever(sslopt = {"cert_reqs": ssl.CERT_NONE})
            except Exception as error:
                logging.error(f"Error in WebSocket connection: {error}")

            if self.running:
                logging.info(f"Reconnecting in {self.reconnect_delay} seconds...")
                time.sleep(self.reconnect_delay)

    def on_open(self, websocket):
        """
        Creates and sends initial WebSocket connection and subscription frames.
        """
        # Send the connection frame to establish communication
        websocket.send(self._create_connect_frame())
        
        # Sends suscription frames to required channels
        channels = ["/notification/alert", f"/notification/readingResult/{Config.CLIENT_ID}"]
        for id, channel in enumerate(channels):
            websocket.send(self._create_subscribe_frame(f"sub-{id}", channel))

    def on_message(self, websocket, message):
        """
        Processes incoming messages and emits the extracted JSON to the UI thread.
        """
        json_message = self._extract_json_from_message(message)
        if json_message:
            self.message_signal.emit(json_message)
            logging.info(f"Received message: {json_message}")

    def on_error(self, websocket, error):
        """
        Handles WebSocket errors and logs them.
        """
        logging.error(f"WebSocket error: {error}")

    def on_close(self, websocket, status_code, message):
        """
        Handles WebSocket closure events and logs the reason for closing.
        """
        logging.info(f"WebSocket closed with code: {status_code}, message: {message}")

    def disconnect(self):
        """
        Stops the WebSocket connection by setting the running flag to False and closing the connection if open.
        """
        self.running = False
        if self.websocket:
            self.websocket.close()

    def send_meter_reading(self, current_usage):
        """
        Sends a meter reading to the server.
        """
        if self.websocket and self.websocket.sock and self.websocket.sock.connected:
            try:
                # Prepare the message payload with client ID, usage, and timestamp
                message = {
                    "clientId": Config.CLIENT_ID,
                    "currentUsage": current_usage,
                    "timestamp": datetime.now().timestamp()
                }
                # Send the formatted frame with the meter reading data
                self.websocket.send(self._create_send_frame("/app/meterReading", message))
            except websocket.WebSocketConnectionClosedException:
                logging.error("Error: Connection is closed. Cannot send message.")
        else:
            logging.warning("Cannot send message, WebSocket is not connected.")
            self.alert_signal.emit("An error occurred while communicating with the server.")

    def _create_connect_frame(self):
        """
        Creates a connection frame required by the WebSocket protocol in order to initiate a connection.
        """
        return (
            "CONNECT\n"
            "accept-version:1.1,1.0\n"
            f"host:{Config.WEBSOCKET_HOST}\n"
            "heart-beat:10000,10000\n\n\0"
        )

    def _create_subscribe_frame(self, id, destination):
        """
        Creates a subscription frame for a specific channel.
        """
        return f"SUBSCRIBE\nid:{id}\ndestination:{destination}\n\n\0"

    def _create_send_frame(self, destination, message):
        """
        Creates a send frame with a specific destination and message.
        """
        message = json.dumps(message)
        return f"SEND\ndestination:{destination}\n\n{message}\n\0"

    def _extract_json_from_message(self, message):
        """
        Finds and extracts JSON content from a received WebSocket message.
        """
        match = re.search(r'\{.*\}', message)
        return match.group(0) if match else None