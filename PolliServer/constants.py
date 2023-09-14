# constants.py
from PolliOS.backend.BackendSingleton import BackendSingleton

# Datetime format string
DATETIME_FORMAT_STRING = "%Y-%m-%dT%H:%M:%S.%f"

# Swarm status constants
LAST_SEEN_THRESHOLD_MINUTES = 10000

# Image constants
THUMBNAIL_SIZE = (150, 150)


# Dependency to get the database session
def get_db():
    backend = BackendSingleton()
    session = backend.session
    db = session()
    try:
        yield db
    finally:
        db.close()