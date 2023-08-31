export REDIS_OM_URL="redis://100.118.87.109:6380/0"
```
import redis
from redis_om import get_redis_connection
r = get_redis_connection()
```


Tested redis methods:

PodRecord
 - @name:{{{pod_name}}}

SpecimenRecord

FrameRecord


Unverified:

FrameRecord
 - podID