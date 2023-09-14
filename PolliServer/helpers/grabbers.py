# PolliOS/PolliServer/helpers/grabbers.py
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
import traceback

from PolliServer.constants import *
from models.models import SpecimenRecord, PodRecord
from PolliServer.logger.logger import LoggerSingleton

logger = LoggerSingleton().get_logger()



async def grab_swarm_status(db: AsyncSession):
    '''
    Get swarm status from PodRecord MySQL database records.
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
    try:
        # Calculate the cutoff time for last_seen
        cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=LAST_SEEN_THRESHOLD_MINUTES)

        # Query records from PodRecord table that have a last_seen time greater than the cutoff time
        # Use select() and await for asynchronous query
        stmt = select(PodRecord).filter(PodRecord.last_seen > cutoff_time)
        result = await db.execute(stmt)
        records = result.scalars().all()
        
        swarm_status = []  # Initialize as a list
        for record in records:

            pod_status = {
                'pod_id': record.name,
                'connection_status': record.connection_status,
                'stream_type': record.stream_type,
                'loc_name': record.location_name,
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
    except Exception as e:
        logger.server_error(f"Error in grab_swarm_status function: {e}")
        traceback.print_exc()  # This will print the traceback to the console.
        # Re-raise the exception so that the calling function can catch it
        raise e



def build_timeline_data_query(db_session, start_date=None, end_date=None, pod_id=None, location=None, 
                             L1_conf_thresh=0.0, L2_conf_thresh=0.0, species_only=False):

    query = db_session.query(SpecimenRecord)

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, DATETIME_FORMAT_STRING)
        end_datetime = datetime.strptime(end_date, DATETIME_FORMAT_STRING)
        query = query.filter(SpecimenRecord.timestamp.between(start_datetime, end_datetime))
    
    if pod_id:
        query = query.filter(SpecimenRecord.podID.in_(pod_id))
    
    if location:
        query = query.filter(SpecimenRecord.loc_name == location)
    
    if L1_conf_thresh:
        query = query.filter(SpecimenRecord.S1_score >= L1_conf_thresh)
    
    if L2_conf_thresh:
        query = query.filter(SpecimenRecord.S2_taxonID_score >= L2_conf_thresh)
    
    if species_only:
        query = query.filter(SpecimenRecord.S2_taxonRank == 'L10')

    # Limiting the results as before
    query = query.limit(5000)
    
    return query

async def grab_timeline_data(db: AsyncSession,
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None,
                             pod_id: Optional[List[str]] = None,
                             location: Optional[str] = None,
                             species_only: Optional[bool] = False,
                             L1_conf_thresh: Optional[float] = 0.0,
                             L2_conf_thresh: Optional[float] = 0.0,
                             incl_images: Optional[bool] = False):

    records_query = build_timeline_data_query(db, start_date, end_date, pod_id, location, 
                                              L1_conf_thresh, L2_conf_thresh, species_only)
    
    records = records_query.all()

    # Handling images is still left as a placeholder. You'll have to add your logic here.
    if incl_images:
        pass

    timeline_data = []
    for record in records:
        record_dict = {
            "id": record.id,
            "timestamp": record.timestamp.strftime(DATETIME_FORMAT_STRING),
            "pod_id": record.podID,
            "swarm_name": record.swarm_name,
            "run_name": record.run_name,
            "loc_name": record.loc_name,
            "loc_lat": record.lat,
            "loc_lon": record.lon,
            "taxonID_str": record.S2_taxonID_str,
            "taxonID_score": record.S2_taxonID_score,
            "taxonRank": record.S2_taxonRank,
            "L1_classification": record.S1_class,
        }
        if incl_images:
            record_dict["image"] = None  # Placeholder, add your image logic here
        timeline_data.append(record_dict)
    
    return timeline_data