import logging
import uvicorn

logging.basicConfig(level=logging.DEBUG)

from PolliServer.server import app

# Start the FastAPI app
uvicorn.run(app, host="0.0.0.0", port=8069, log_level="debug")