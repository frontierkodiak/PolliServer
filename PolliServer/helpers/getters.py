# getters.py
# For smaller requests: Getting list for UI dropdowns, helpers within grabbers, etc.

from typing import Optional, List
from fastapi import FastAPI, Query
from redis_om import NotFoundError
import datetime
import base64
import cv2

from PolliServer.constants import *
from PolliServer.utils import *

# from redisJsonRecord import *
from recordModels import *


async def L10_taxonID_strs_getter():
    # Get all SpecimenRecords
    records = SpecimenRecord.all_pks()
    
    # Extract unique L10_taxonID_str values 
    taxon_strs = set()
    for pk in records:
        record = SpecimenRecord.get(pk)
        if record.taxa.L10_taxonID_str:
            taxon_strs.add(record.taxa.L10_taxonID_str)

    # CLARIFY: How do we want to sort these? Most common? Most recent?

    return list(taxon_strs)

async def pod_ids_getter():
    # Get all SpecimenRecords
    records = SpecimenRecord.all_pks()
    
    # Extract unique pod_id values 
    pod_ids = set()
    for pk in records:
        record = SpecimenRecord.get(pk)
        if record.frame.podID:
            pod_ids.add(record.frame.podID)
    print(f"pod_ids: {pod_ids}")

    # Alphabetize
    pod_ids = sorted(pod_ids)
    print(f"sorted pod_ids: {pod_ids}")

    return list(pod_ids)

async def locations_getter():
    # Get all SpecimenRecords
    records = SpecimenRecord.all_pks()
    
    # Extract unique loc_name values 
    locations = set()
    for pk in records:
        record = SpecimenRecord.get(pk)
        if record.location.loc_name:
            locations.add(record.location.loc_name)

    # Alphabetize
    locations = sorted(locations)

    return list(locations)

async def swarms_getter():
    # Get all SpecimenRecords
    records = SpecimenRecord.all_pks()
    
    # Extract unique swarm_name values 
    swarms = set()
    for pk in records:
        record = SpecimenRecord.get(pk)
        if record.frame.swarm_name:
            swarms.add(record.frame.swarm_name)

    # Alphabetize
    swarms = sorted(swarms)

    return list(swarms)

async def runs_getter():
    # Get all SpecimenRecords
    records = SpecimenRecord.all_pks()
    
    # Extract unique run_name values 
    runs = set()
    for pk in records:
        record = SpecimenRecord.get(pk)
        if record.frame.run_name:
            runs.add(record.frame.run_name)

    # Alphabetize
    runs = sorted(runs)

    return list(runs)


async def dates_getter():
    # Get all SpecimenRecords
    records = SpecimenRecord.all_pks()

    # Extract unique date values from timestamps
    date_set = set()
    for pk in records:
        record = SpecimenRecord.get(pk)
        if record.frame.timestamp:
            date_obj = record.frame.timestamp.date()  # Get the date part directly
            date_set.add(date_obj)

    # Sort the dates
    sorted_dates = sorted(date_set)

    return sorted_dates

