import databases
from PolliOS.logger import LoggerSingleton

logger = LoggerSingleton().get_logger()

class ServerBackendSingleton:
    _instance = None
    _async_database = None

    def __new__(cls, db_config=None):
        if cls._instance is None:
            logger.info("Creating a new ServerBackendSingleton instance...")
            cls._instance = super(ServerBackendSingleton, cls).__new__(cls)

            if db_config:
                async_connection_string = f"mysql+aiomysql://{db_config['user']}:{db_config['password']}@{db_config['address']}:{db_config['port']}/{db_config['database']}"
                logger.info(f"Async Backend connection string: {async_connection_string}")
                
                try:
                    cls._instance._async_database = databases.Database(async_connection_string)
                    logger.info("Successfully created async database connection!")
                except Exception as e:
                    logger.error(f"Failed to create async database connection. Error: {e}")

        return cls._instance

    @property
    def async_database(self):
        return self._async_database

    @async_database.setter
    def async_database(self, value):
        self._async_database = value
