import redis
from redis.commands.json.path import Path
import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import NumericFilter, Query
from typing import List, Optional


from PolliServer.constants import DATETIME_FORMAT_STRING, r, r_img, THUMBNAIL_SIZE
from redisJsonRecord import *

class RedisJsonHelper:

    def __init__(self):
        pass

    def filter_by_date(self, start_date: Optional[str], end_date: Optional[str]) -> List[str]:
        # We'll come back to this later.
        results = FrameRecord.find(FrameRecord.frame.timestamp >= start_date, FrameRecord.frame.timestamp <= end_date).all()
        return [record.id for record in results]

    def filter_by_pod_id(self, pod_id: List[str]) -> List[str]:
        results = []
        for pid in pod_id:
            results.extend(FrameRecord.find(FrameRecord.frame.podID == pid).all())
        return [record.id for record in results]

    def filter_by_location(self, location: str) -> List[str]:
        results = FrameRecord.find(FrameRecord.location.loc_name == location).all()
        return [record.id for record in results]

    def filter_species_only(self) -> List[str]:
        results = SpecimenRecord.find(SpecimenRecord.taxa.L10_taxonID_str != None).all()
        return [record.id for record in results]

    def filter_by_L1_conf_thresh(self, L1_conf_thresh: float) -> List[str]:
        results = SpecimenRecord.find(SpecimenRecord.L1Card.score >= L1_conf_thresh).all()
        return [record.id for record in results]

    def filter_by_L2_conf_thresh(self, L2_conf_thresh: float) -> List[str]:
        results = SpecimenRecord.find(SpecimenRecord.L2Card.score >= L2_conf_thresh).all()
        return [record.id for record in results]

    def get_unique_values(self, path: str) -> List[str]:
        # This method might be a bit more complex with redis-om.
        # Since direct querying like this might not be straightforward, 
        # consider fetching all records and then extracting the unique values using Python.
        # Alternatively, you can use the `redis_conn` approach to run Redis commands directly.
        pass

    async def L10_taxonID_strs_getter(self):
        return self.get_unique_values('.taxa.L10_taxonID_str')

    async def pod_ids_getter(self):
        return self.get_unique_values('.frame.podID')

    async def locations_getter(self):
        return self.get_unique_values('.location.loc_name')

    async def swarms_getter(self):
        return self.get_unique_values('.frame.swarm_name')

    async def runs_getter(self):
        return self.get_unique_values('.frame.run_name')

    async def dates_getter(self):
        records = self._json_query('SpecimenRecord.*')
        dates = {self._json_query(record, '.frame.timestamp.date()') for record in records if self._json_query(record, '.frame.timestamp')}
        return sorted(dates)