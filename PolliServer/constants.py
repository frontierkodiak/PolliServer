# constants.py
from redis_om import get_redis_connection
# Datetime format string
DATETIME_FORMAT_STRING = "%Y-%m-%dT%H:%M:%S.%f"

# Redis connection
redis = get_redis_connection()
redis_img = get_redis_connection(db=1) # DEV: Need to unify with ImageDB connection specified in backend config.

# Image constants
THUMBNAIL_SIZE = (150, 150)