import redis
from typing import List, Optional

class RedisJsonHelper:

    def __init__(self, client: redis.client):
        self.client = client

    def _json_query(self, *args) -> List[str]:
        # This is a pseudocode method.
        # Use the actual method from your Redis client to perform the RedisJSON query.
        return self.client._json_query(*args)

    def filter_by_date(self, records: List[str], start_date: Optional[str], end_date: Optional[str]) -> List[str]:
        if start_date:
            records = self._json_query('.frame.timestamp', '>=', start_date)
        if end_date:
            records = self._json_query('.frame.timestamp', '<=', end_date)
        return records

    def filter_by_pod_id(self, records: List[str], pod_id: List[str]) -> List[str]:
        return [pk for pk in records if self._json_query(pk, '.frame.podID') in pod_id]

    def filter_by_location(self, records: List[str], location: str) -> List[str]:
        return [pk for pk in records if self._json_query(pk, '.location.loc_name') == location]

    def filter_species_only(self, records: List[str]) -> List[str]:
        return [pk for pk in records if self._json_query(pk, '.taxa.L10_taxonID_str')]

    def filter_by_L1_conf_thresh(self, records: List[str], L1_conf_thresh: float) -> List[str]:
        return [pk for pk in records if self._json_query(pk, '.L1Card.score') >= L1_conf_thresh]

    def filter_by_L2_conf_thresh(self, records: List[str], L2_conf_thresh: float) -> List[str]:
        return [pk for pk in records if self._json_query(pk, '.L2Card.score') >= L2_conf_thresh]

    def get_unique_values(self, path: str) -> List[str]:
            records = self._json_query('SpecimenRecord.*')  # Assuming SpecimenRecord is the root key for the data
            unique_values = {self._json_query(record, path) for record in records if self._json_query(record, path)}
            return sorted(unique_values)

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