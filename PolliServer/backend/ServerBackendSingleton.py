# PolliServer/backend/ServerBackendSingleton.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from PolliServer.logger.logger import LoggerSingleton

logger = LoggerSingleton().get_logger()

class ServerBackendSingleton:
    _instance = None
    _async_sessionmaker = None

    def __new__(cls, db_config=None):
        if cls._instance is None:
            logger.info("Creating a new ServerBackendSingleton instance...")

            cls._instance = super(ServerBackendSingleton, cls).__new__(cls)
            if db_config:
                async_connection_string = f"mysql+aiomysql://{db_config['user']}:{db_config['password']}@{db_config['address']}:{db_config['port']}/{db_config['database']}"
                logger.info(f"Async Backend connection string: {async_connection_string}")

                try:
                    engine = create_async_engine(async_connection_string, echo=True)
                    cls._instance._async_sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
                    logger.info("Successfully created async sessionmaker!")
                except Exception as e:
                    logger.error(f"Failed to create async sessionmaker. Error: {e}")

        return cls._instance

    @property
    def async_sessionmaker(self):
        return self._async_sessionmaker
