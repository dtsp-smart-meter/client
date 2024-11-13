from dotenv import load_dotenv
import uuid
import os

load_dotenv()

class Config:
    WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST")
    WEBSOCKET_PORT = os.getenv("WEBSOCKET_PORT")
    WEBSOCKET_URL = f"wss://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}/ws"
    CLIENT_ID = os.getenv("CLIENT_ID", str(uuid.uuid4())) # If CLIENT_ID environment variable is set, use that, otherwise generate a random one
    API_KEY = os.getenv("API_KEY")