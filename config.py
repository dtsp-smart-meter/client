from dotenv import load_dotenv
import uuid
import os

load_dotenv()

class Config:
    WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST")
    WEBSOCKET_PORT = os.getenv("WEBSOCKET_PORT")
    WEBSOCKET_URL = f"wss://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}/ws"
    CA_CERT_PATH = os.getenv("CA_CERT_PATH") # The CA certificate to connect to the server using SSL
    CLIENT_ID = os.getenv("CLIENT_ID", str(uuid.uuid4())) # If CLIENT_ID environment variable is set, use that, otherwise generate a random one
    AUTHENTICATION_TOKEN = os.getenv("AUTHENTICATION_TOKEN")