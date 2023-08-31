from typing import Optional, List
from fastapi import FastAPI, Query
from redis_om import NotFoundError
import datetime
import base64
import cv2

from PolliServer.constants import *
from PolliServer.helpers.redis_json_helper import RedisJsonHelper
from PolliServer.utils import *

# from redisJsonRecord import *
from recordModels import *
from PolliOS_utils import get_image_from_redis, crop_image_absolute_coords



async def build_timeline_data_query(start_date=None, end_date=None, pod_id=None, location=None, L1_conf_thresh=0.0, L2_conf_thresh=0.0, species_only=False):
    """
    Searches for SpecimenRecords matching the given parameters.
    """
    query_parts = []
    
    if start_date and end_date:
        query_parts.append(f"@timestamp:[{start_date} {end_date}]")
    
    if pod_id:
        pod_ids = "|".join(pod_id)
        query_parts.append(f"@podID:{{'{pod_ids}'}}")
    
    if location:
        query_parts.append(f"@loc_name:{{'{location}'}}")

    if L1_conf_thresh:
        query_parts.append(f"@S1_score:[{L1_conf_thresh} +inf]")

    if L2_conf_thresh:
        query_parts.append(f"@S2_taxonID_score:[{L2_conf_thresh} +inf]")

    if species_only:
        query_parts.append(f"@S2_taxonRank:{{L10}}")

    return " ".join(query_parts)


async def grab_timeline_data(start_date: Optional[str] = None,
                      end_date: Optional[str] = None,
                        pod_id: Optional[List[str]] = None,
                        location: Optional[str] = None,
                        species_only: Optional[bool] = False,
                        L1_conf_thresh: Optional[float] = 0.0,
                        L2_conf_thresh: Optional[float] = 0.0,
                        incl_images: Optional[bool] = False):
    """
    Get timeline data from Redis.
    1) Get all SpecimenRecords
    2) Filter by start_date and end_date
    3) Filter by pod_id/s
    4) Filter by location (location_name) FUTURE: lat/lon
    5) Optionally include images
        1) Get all ImageRecords for SpecimenRecords
        2) Crop to detection bbox
        3) Resize to thumbnail size
        4) Convert to base64
    6) Return JSON
    """

    rj = RedisJsonHelper(r)

    # Build and execute the query
    query = await build_query(start_date, end_date, pod_id, location, L1_conf_thresh, L2_conf_thresh, species_only)
    results = r.execute_command('FT.SEARCH', 'SpecimenRecord_index', query)

    records = [res for i, res in enumerate(results) if i % 2 != 0]  # Parse the results to get only the records


    # Optionally include images
    if incl_images:
        # Get all ImageRecords for SpecimenRecords
        prepped_imgs = []
        for pk in records:
            try:
                img_pk = SpecimenRecord.get(pk).media.pk
                img = get_image_from_redis(img_pk, r_img, output_format='cv2')
                # Crop to detection bbox
                # HACK: These are absolute coords! Supposed to be relative.
                bbox_LL_abs = SpecimenRecord.get(pk).detection.bboxLL
                bbox_UR_abs = SpecimenRecord.get(pk).detection.bboxUR
                cropped_img = crop_image_absolute_coords(img, bbox_LL_abs, bbox_UR_abs)
                # Resize to thumbnail size
                resized_img = cv2.resize(cropped_img, THUMBNAIL_SIZE)
                # Convert to base64
                retval, buffer = cv2.imencode('.jpg', resized_img)
                jpg_as_text = base64.b64encode(buffer)
                prepped_imgs.append(jpg_as_text)
            except NotFoundError:
                prepped_imgs.append(None)

    # Prepare data for JSON serialization
    timeline_data = []
    for i, pk in enumerate(records):
        record = SpecimenRecord.get(pk)
        record_dict = {
            # add all relevant record attributes you want to include in the response
            # ensure all added elements are JSON serializable (e.g., convert datetime to string if needed)
            "id": pk,
            "timestamp": record.frame.timestamp.strftime(DATETIME_FORMAT_STRING),
            "pod_id": record.frame.podID,
            "swarm_name": record.frame.swarm_name,
            "run_name": record.frame.run_name,
            "loc_name": record.location.loc_name,
            "loc_lat": record.location.lat,
            "loc_lon": record.location.lon,
            "taxonID_str": record.taxa.taxonID_str,
            "taxonID_score": record.taxa.taxonID_score,
            "taxonRank": record.taxa.taxonRank,
            "L1_classification": record.L1Card.classification,
        }
        if incl_images:
            record_dict["image"] = prepped_imgs[i]  # append corresponding image or None if NotFoundError was raised
        timeline_data.append(record_dict)

    # Return JSON...
    return timeline_data


async def grab_swarm_status():
    '''
    Get swarm status from PodRecord Redis objects.
    Returns JSON swarm_status list with the following object values:
        - pod_id
        - connection_status
        - stream_type
        - loc_name
        - loc_lat
        - loc_lon
        - queue_length
        - total_frames
        - last_L1_class
        - last_L2_class
        - total_specimens
        - last_specimen_created_time
    '''
    records = PodRecord.all_pks()

    swarm_status = []  # Initialize as a list
    for pk in records:
        record = PodRecord.get(pk)
        
        pod_status = {
            'pod_id': record.name,  # Assuming the podID is inside frame
            'connection_status': record.connection_status,
            'stream_type': record.stream_type,
            'loc_name': record.location_name,  # Assuming location data is structured similarly to SpecimenRecord
            'loc_lat': record.latitude,
            'loc_lon': record.longitude,
            'queue_length': record.queue_length,
            'total_frames': record.total_frames,
            'last_L1_class': record.last_L1_class,
            'last_L2_class': record.last_L2_class,
            'total_specimens': record.total_specimens,
            'last_specimen_created_time': record.last_specimen_created_time.strftime(DATETIME_FORMAT_STRING) if record.last_specimen_created_time else None
        }
        swarm_status.append(pod_status)  # Append each status object to the list

    return swarm_status
