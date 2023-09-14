import logging
import uvicorn

logging.basicConfig(level=logging.DEBUG)

from PolliServer.server import app
from PolliServer.backend.initialize_backend import initialize_backend_from_config

# Initialize the ServerBackendSingleton using the config
initialize_backend_from_config()

# Start the FastAPI app
uvicorn.run(app, host="0.0.0.0", port=8069, log_level="debug")
