from dotenv import load_dotenv
import uuid
import os

# Load environment variables from the `.env` file.
load_dotenv()

class Config:
    # Retrieve the WebSocket host address from the environment variable `WEBSOCKET_HOST`.
    WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST")
    # Retrieve the WebSocket port number from the environment variable `WEBSOCKET_PORT`.
    WEBSOCKET_PORT = os.getenv("WEBSOCKET_PORT")
    # Construct the WebSocket URL using the host and port values.
    WEBSOCKET_URL = f"wss://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}/ws"

    # Retrieve the path to the CA (Certificate Authority) certificate used for SSL connections from the environment variable `CA_CERT_PATH`.
    CA_CERT_PATH = os.getenv("CA_CERT_PATH")
    
    # Retrieve the client ID from the environment variable `CLIENT_ID`.
    # If the environment variable is not set, generate a random UUID.
    CLIENT_ID = os.getenv("CLIENT_ID", str(uuid.uuid4()))
    # Retrieve the authentication token from the environment variable `AUTHENTICATION_TOKEN`.
    AUTHENTICATION_TOKEN = os.getenv("AUTHENTICATION_TOKEN")