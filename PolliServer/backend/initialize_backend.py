# initialize_backend.py

import yaml
from PolliServer.backend.ServerBackendSingleton import ServerBackendSingleton
from PolliServer.logger.logger import LoggerSingleton

logger = LoggerSingleton().get_logger()

def initialize_backend_from_config(config_path):
    
    # Load and read the YAML file
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)

    # Extract the first database config (assuming it's the only one for now)
    db_config = config_data['databases'][0]

    if db_config['type'] != 'mysql':
        logger.server_error(f"Unsupported database type: {db_config['type']}")
        return
    
    # Create the ServerBackendSingleton using the extracted parameters
    ServerBackendSingleton(
        db_config={
            'address': db_config['address'],
            'port': db_config['port'],
            'user': db_config['user'],
            'password': db_config['password'],
            'database': db_config['database']
        }
    )
    logger.server_info("ServerBackendSingleton initialized!")
