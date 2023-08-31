# constants.py
from redis_om import get_redis_connection
# Datetime format string
DATETIME_FORMAT_STRING = "%Y-%m-%dT%H:%M:%S.%f"

# Redis connection
r = get_redis_connection()
r_img = get_redis_connection(db=1) # DEV: Need to unify with ImageDB connection specified in backend config.

# Redis indices
PodRecord_index = ":PolliOS.engine.records.recordModels.PodRecord:index"
FrameRecord_index = ":PolliOS.engine.records.recordModels.FrameRecord:index"
SpecimenRecord_index = ":PolliOS.engine.records.recordModels.SpecimenRecord:index"
ImageRecord_index = ":PolliOS.engine.records.recordModels.ImageRecord:index"

# Image constants
THUMBNAIL_SIZE = (150, 150)