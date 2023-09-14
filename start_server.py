import logging
import uvicorn
import argparse

logging.basicConfig(level=logging.DEBUG)

from PolliServer.server import app
from PolliServer.backend.initialize_backend import initialize_backend_from_config

def main(config):
    # Initialize the ServerBackendSingleton using the config
    initialize_backend_from_config(config)

    # Start the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8069, log_level="debug")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the configuration file")
    args = parser.parse_args()
    main(args.config)
