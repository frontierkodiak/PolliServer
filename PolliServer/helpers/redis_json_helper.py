import redis
from redis.commands.json.path import Path
import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import NumericFilter, Query
from typing import List, Set, Optional
import json


from PolliServer.constants import *
# from redisJsonRecord import *
from recordModels import *


class RedisJsonHelper:

    def __init__(self):
        pass

    def filter_by_date(self, start_date: Optional[str], end_date: Optional[str]) -> List[str]:
        # We'll come back to this later.
        results = FrameRecord.find(FrameRecord.frame.timestamp >= start_date, FrameRecord.frame.timestamp <= end_date).all()
        return [record.id for record in results]
    
    
    def filter_podrecords_by_pod_name(self, pod_name: str) -> List[str]:
        query = f'@name:{{{pod_name}}}'
        result = r.execute_command('FT.SEARCH', PodRecord_index, query, 'NOCONTENT')
        return result[1::1]
    
    def filter_specimenrecords_by_podID(self, pod_name: str) -> List[str]:
        query = f'@podID:{{{pod_name}}}'
        result = r.execute_command('FT.SEARCH', SpecimenRecord_index, query, 'NOCONTENT')
        return result[1::1]

    def filter_framerecords_by_pod_id(self, pod_id: str) -> List[str]:
        query = f'@podID:{{{pod_id}}}'
        result = r.execute_command('FT.SEARCH', FrameRecord_index, query, 'NOCONTENT')
        return result[1::1]

    def filter_framerecords_by_location(self, location: str) -> List[str]:
        query = f"@loc_name:{{{location}}}"
        results = r.execute_command('FT.SEARCH', FrameRecord_index, query, 'NOCONTENT')
        return results[1::1]

    def filter_specimens_by_S2_taxonRank(self, taxon_rank: str) -> List[str]:
        query = f"@S2_taxonRank:{{{taxon_rank}}}"
        results = r.execute_command('FT.SEARCH', SpecimenRecord_index, query)
        return results[1::1]

    def filter_specimenrecords_by_S1_score(self, L1_conf_thresh: float) -> List[str]:
        query = f"@S1_score:[{L1_conf_thresh} +inf]"
        results = r.execute_command('FT.SEARCH', SpecimenRecord_index, query, 'NOCONTENT')
        return results[1::1]

    def filter_specimenrecords_by_S2_taxonID_score(self, L2_conf_thresh: float) -> List[str]:
        query = f"@S2_taxonID_score:[{L2_conf_thresh} +inf]"
        results = r.execute_command('FT.SEARCH', SpecimenRecord_index, query, 'NOCONTENT')
        return results[1::1]
    
    def get_unique_values(self, index: str, field_name: str) -> Set[str]:
        result = r.execute_command('FT.SEARCH', index, "*", "LIMIT", "0", "1000")
        
        record_values = result[2::2]
        unique_values = set()

        for record_data in record_values:
            json_string = record_data[1]
            data_dict = json.loads(json_string)
            value = data_dict.get(field_name)
            if value:
                unique_values.add(value)
        
        return unique_values

    def get_unique_date_values(self, index: str, field_name: str) -> Set[str]:
        result = r.execute_command('FT.SEARCH', index, "*", "LIMIT", "0", "1000")
        
        record_values = result[2::2]
        unique_dates = set()

        for record_data in record_values:
            json_string = record_data[1]
            data_dict = json.loads(json_string)
            datetime_value = data_dict.get(field_name)
            if datetime_value:
                # Convert the datetime string to a date object and then add it to the set
                date_only = datetime_value.split('T')[0]  # Assuming it's in the format "YYYY-MM-DDTHH:MM:SS"
                unique_dates.add(date_only)
        
        return unique_dates

    

    
    
    
    
    
    
    
    
    
        # def get_unique_podIDs_framerecord(self) -> Set[str]:
        # result = r.execute_command('FT.SEARCH', FrameRecord_index, "*", "LIMIT", "0", "1000")
        
        # # Parse the result. For every record, every even index is a key and odd index is a value.
        # # Assuming that the values are stored as serialized JSON strings in Redis, 
        # # we need to deserialize them to extract the name field.
        # import json

        # # Extract all the JSON values
        # record_values = result[2::2]
        
        # names = set()

        # # Loop through each record's data
        # for record_data in record_values:
        #     # The first item (index 0) is the field name, 
        #     # the second item (index 1) is the serialized JSON string
        #     json_string = record_data[1]
            
        #     # Deserialize the JSON string to a Python dictionary
        #     data_dict = json.loads(json_string)
            
        #     # Add the 'name' value to our set, ensuring uniqueness
        #     name_value = data_dict.get('podID')
        #     if name_value:  # This checks if the name value is not None or empty
        #         names.add(name_value)
        
        # return names
        
        
    # def get_unique_pod_names_podrecord(self) -> Set[str]:
    #     result = r.execute_command('FT.SEARCH', PodRecord_index, "*", "LIMIT", "0", "1000")
        
    #     # Parse the result. For every record, every even index is a key and odd index is a value.
    #     # Assuming that the values are stored as serialized JSON strings in Redis, 
    #     # we need to deserialize them to extract the name field.
    #     import json

    #     # Extract all the JSON values
    #     record_values = result[2::2]
        
    #     names = set()

    #     # Loop through each record's data
    #     for record_data in record_values:
    #         # The first item (index 0) is the field name, 
    #         # the second item (index 1) is the serialized JSON string
    #         json_string = record_data[1]
            
    #         # Deserialize the JSON string to a Python dictionary
    #         data_dict = json.loads(json_string)
            
    #         # Add the 'name' value to our set, ensuring uniqueness
    #         name_value = data_dict.get('name')
    #         if name_value:  # This checks if the name value is not None or empty
    #             names.add(name_value)
        
    #     return names
    
        # def get_unique_podIDs_specimenrecord(self) -> Set[str]:
        # result = r.execute_command('FT.SEARCH', SpecimenRecord_index, "*", "LIMIT", "0", "1000")
        
        # # Parse the result. For every record, every even index is a key and odd index is a value.
        # # Assuming that the values are stored as serialized JSON strings in Redis, 
        # # we need to deserialize them to extract the name field.
        # import json

        # # Extract all the JSON values
        # record_values = result[2::2]
        
        # names = set()

        # # Loop through each record's data
        # for record_data in record_values:
        #     # The first item (index 0) is the field name, 
        #     # the second item (index 1) is the serialized JSON string
        #     json_string = record_data[1]
            
        #     # Deserialize the JSON string to a Python dictionary
        #     data_dict = json.loads(json_string)
            
        #     # Add the 'name' value to our set, ensuring uniqueness
        #     name_value = data_dict.get('podID')
        #     if name_value:  # This checks if the name value is not None or empty
        #         names.add(name_value)
        
        # return names