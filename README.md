# Smart Meter Client

Python PyQT5 client for the Smart Meter.

## Installation and Setup

### Requirements

- Python 3.7+

### Step-by-Step Setup

1. **Clone the repository**:

```bash
git clone https://github.com/dtsp-smart-meter/client.git
cd client
```

2. **Create and activate a virtual environment**:

```bash
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

3. **Install required dependencies**:

```bash
pip3 install -r requirements.txt
```

4. **Configure environment variables**:

Create a `.env` file in the project root and add your configuration:

```makefile
WEBSOCKET_HOST=localhost
WEBSOCKET_PORT=8443
CA_CERT_PATH=/Documents/SmartMeter/server/smartmeter_ca_cert.pem
AUTHENTICATION_TOKEN=
```

5. **Run the application**:

```bash
python3 main.py
```