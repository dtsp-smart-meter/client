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
    This class runs on a separate thread to avoid blocking the main UI thread.
    """
    
    # Define PyQt signals to communicate with the main UI thread.
    connected_signal = pyqtSignal() # Emitted when WebSocket is connected.
    message_signal = pyqtSignal(str) # Emitted when a message is received.
    alert_signal = pyqtSignal(str) # Emitted to show an alert in the UI.

    def __init__(self):
        super().__init__()
        self.websocket = None
        self.running = False # Flag to control the running state of the WebSocket connection thread.
        self.reconnect_delay_seconds = 5 # Delay (in seconds) before attempting to reconnect after a failure.

    def connect(self):
        """
        Starts the WebSocket connection by setting the running flag to True and starting the connection thread.
        """

        self.running = True
        self.start() # Start the WebSocket connection in a separate thread.

    def run(self):
        """
        The main thread loop: continuously attempts to establish the WebSocket connection and
        automatically reconnects if the connection is lost.
        """

        while self.running:
            try:
                # Initialize and configure the WebSocket client.
                self.websocket = websocket.WebSocketApp(
                    Config.WEBSOCKET_URL, # WebSocket server URL from config.
                    on_open = self.on_open, # Method to call when the connection opens.
                    on_message = self.on_message, # Method to call when a message is received.
                    on_error = self.on_error, # Method to call when an error occurs.
                    on_close = self.on_close # Method to call when the connection closes.
                )
                
                # Run the WebSocket in blocking mode with SSL.
                self.websocket.run_forever(sslopt = {
                    "ca_certs": Config.CA_CERT_PATH, # Path to CA certificate for SSL verification.
                    "cert_reqs": ssl.CERT_REQUIRED, # Require SSL certificate validation.
                    "ssl_version": ssl.PROTOCOL_TLSv1_2 # SSL/TLS version.
                })
            except Exception as error:
                logging.error(f"Error in WebSocket connection: {error}")

            # If the running flag is still True, attempt to reconnect after a delay.
            if self.running:
                logging.info(f"Reconnecting in {self.reconnect_delay_seconds} seconds...")
                time.sleep(self.reconnect_delay_seconds)

    def on_open(self, websocket):
        """
        This method is called when the WebSocket connection is successfully opened.
        It sends initial frames for connection and subscribes to necessary channels.
        """

        # Send the initial connection frame to establish communication.
        websocket.send(self._create_connect_frame())
        
        # List of channels to subscribe to, including client-specific channels.
        channels = [
            "/notification/alert",
            f"/notification/alert/{Config.CLIENT_ID}",
            f"/notification/readingResult/{Config.CLIENT_ID}"
        ]
        
        # Subscribe to each channel by sending the respective subscription frame.
        for id, channel in enumerate(channels):
            websocket.send(self._create_subscribe_frame(f"sub-{id}", channel))
        
        # Emit signal to notify UI that connection is established and channels have been subscribed to.
        self.connected_signal.emit()

    def on_message(self, websocket, message):
        """
        This method is called when a message is received through the WebSocket.
        It processes the message and passes it to the UI thread.
        """

        # Extract JSON data from the received WebSocket message.
        json_message = self._extract_json_from_message(message)

        # If a valid JSON message is found, emit it to the UI.
        if json_message:
            self.message_signal.emit(json_message)
            logging.info(f"Received message: {json_message}")

    def on_error(self, websocket, error):
        """
        This method is called when there is an error with the WebSocket connection.
        It logs the error message.
        """

        logging.error(f"WebSocket error: {error}")

    def on_close(self, websocket, status_code, message):
        """
        This method is called when the WebSocket connection is closed.
        It logs the status code and message for debugging purposes.
        """

        logging.info(f"WebSocket closed with code: {status_code}, message: {message}")

    def disconnect(self):
        """
        Stops the WebSocket connection by setting the running flag to False
        and closing the WebSocket connection if it's open.
        """

        self.running = False

        if self.websocket:
            self.websocket.close()

    def send_meter_reading(self, current_usage):
        """
        Sends a meter reading to the server.
        If the WebSocket is connected, it sends the message; otherwise, it shows an alert.
        """

        # Check if the WebSocket is connected and the socket is open.
        if self.websocket and self.websocket.sock and self.websocket.sock.connected:
            try:
                # Prepare the message payload with current usage and timestamp.
                message = {
                    "currentUsage": current_usage,
                    "timestamp": datetime.now().timestamp() # Current UNIX timestamp.
                }

                # Send the meter reading frame to the server.
                self.websocket.send(self._create_send_frame("/app/meterReading", message))
            except websocket.WebSocketConnectionClosedException:
                logging.error("Error: Connection is closed. Cannot send message.")
        else:
            # Log a warning and emit an alert signal if WebSocket is not connected.
            logging.warning("Cannot send message, WebSocket is not connected.")
            self.alert_signal.emit("An error occurred while communicating with the server.")

    def _create_connect_frame(self):
        """
        Creates the connection frame required by the WebSocket protocol to initiate the connection.
        """

        return (
            "CONNECT\n"
            "accept-version:1.1,1.0\n"
            f"host:{Config.WEBSOCKET_HOST}\n"
            "heart-beat:10000,10000\n\n\0"
        )

    def _create_subscribe_frame(self, id, destination):
        """
        Creates the subscription frame for a specific channel to subscribe to.
        """

        return (
            "SUBSCRIBE\n"
            f"id:{id}\n"
            f"destination:{destination}\n\n\0"
        )

    def _create_send_frame(self, destination, message):
        """
        Creates a send frame that will carry a specific message to a destination.
        The frame includes client ID and auth token in the header.
        """

        return (
            f"SEND\n"
            f"destination:{destination}\n"
            f"clientId:{Config.CLIENT_ID}\n"
            f"authToken:{Config.AUTHENTICATION_TOKEN}\n"
            f"\n{json.dumps(message)}\n\0"
        )

    def _extract_json_from_message(self, message):
        """
        Extracts JSON content from a received WebSocket message using regular expressions.
        This function looks for a JSON object in the message string.
        """

        match = re.search(r'\{.*\}', message) # Search for the first occurrence of a JSON object.
        return match.group(0) if match else None # Return the JSON string if found, otherwise None.