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
        - podID
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
        - last_seen
    '''
    try:
        # Calculate the cutoff time for last_seen
        cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=LAST_SEEN_THRESHOLD_MINUTES)

        # Query records from PodRecord table that have a last_seen time greater than the cutoff time
        # Use select() and await for asynchronous query
        stmt = select(PodRecord).filter(PodRecord.last_seen > cutoff_time)
        result = await db.execute(stmt)
        records = result.scalars().all()

        if not records:  # If there are no records, return a list with a single status object with all fields as None
            return [{
                'podID': None,
                'connection_status': None,
                'rssi': None,
                'stream_type': None,
                'loc_name': None,
                'loc_lat': None,
                'loc_lon': None,
                'queue_length': None,
                'total_frames': None,
                'last_S1_class': None,
                'last_S2_class': None,
                'total_specimens': None,
                'last_specimen_created_time': None,
                'last_seen': None,
                'time_since_last_seen': None,
                'time_since_last_specimen': None
            }]

        swarm_status = []  # Initialize as a list
        for record in records:
            
            if record.last_seen:
                time_since_last_seen = datetime.datetime.utcnow() - record.last_seen
            else:
                time_since_last_seen = 0
            if record.last_specimen_created_time:
                time_since_last_specimen = datetime.datetime.utcnow() - record.last_specimen_created_time
            else:
                time_since_last_specimen = 0

            pod_status = {
                'podID': record.name,
                'connection_status': record.connection_status,
                'rssi': record.rssi,
                'stream_type': record.stream_type,
                'loc_name': record.location_name,
                'loc_lat': record.latitude,
                'loc_lon': record.longitude,
                'queue_length': record.queue_length,
                'total_frames': record.total_frames,
                'last_S1_class': record.last_S1_class,
                'last_S2_class': record.last_S2_class,
                'total_specimens': record.total_specimens,
                'last_specimen_created_time': record.last_specimen_created_time.strftime(DATETIME_FORMAT_STRING) if record.last_specimen_created_time else None,
                'last_seen': record.last_seen.strftime(DATETIME_FORMAT_STRING) if record.last_seen else None,
                'time_since_last_seen': time_since_last_seen.total_seconds() / 60.0 if record.last_seen else None,
                'time_since_last_specimen': time_since_last_specimen.total_seconds() / 60.0 if record.last_specimen_created_time else None
            }
            swarm_status.append(pod_status)  # Append each status object to the list

        return swarm_status
    except Exception as e:
        logger.server_error(f"Error in grab_swarm_status function: {e}")
        traceback.print_exc()  # This will print the traceback to the console.
        # Re-raise the exception so that the calling function can catch it
        raise e


def build_timeline_data_query(db_session, start_date=None, end_date=None, podID=None, location=None, 
                             S1_score_thresh=0.0, S2_score_thresh=0.0, S2a_score_thresh=0.0, species_only=False):

    query = db_session.query(SpecimenRecord)

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, DATETIME_FORMAT_STRING)
        end_datetime = datetime.strptime(end_date, DATETIME_FORMAT_STRING)
        query = query.filter(SpecimenRecord.timestamp.between(start_datetime, end_datetime))
    
    if podID:
        query = query.filter(SpecimenRecord.podID.in_(podID))
    
    if location:
        query = query.filter(SpecimenRecord.loc_name == location)
    
    if S1_score_thresh > 0.0:
        query = query.filter(SpecimenRecord.S1_score >= S1_score_thresh)
    
    if S2_score_thresh > 0.0:
        query = query.filter(SpecimenRecord.S2_taxonID_score >= S2_score_thresh)
        
    if S2a_score_thresh > 0.0:
        query = query.filter(SpecimenRecord.S2a_score >= S2a_score_thresh)
    
    if species_only:
        query = query.filter(SpecimenRecord.S2_taxonRank == 'L10')

    # Limiting the results as before
    query = query.limit(5000)
    
    return query

async def grab_timeline_data(db: AsyncSession,
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None,
                             podID: Optional[List[str]] = None,
                             location: Optional[str] = None,
                             species_only: Optional[bool] = False,
                             S1_score_thresh: Optional[float] = 0.0,
                             S2_score_thresh: Optional[float] = 0.0,
                             S2a_score_thresh: Optional[float] = 0.0,
                             incl_images: Optional[bool] = False):

    records_query = build_timeline_data_query(db, start_date, end_date, podID, location, 
                                              S1_score_thresh, S2_score_thresh, S2a_score_thresh, species_only)
    
    records = records_query.all()

    # Handling images is still left as a placeholder. You'll have to add your logic here.
    if incl_images:
        pass

    timeline_data = []
    for record in records:
        record_dict = {
            "timestamp": record.timestamp.strftime(DATETIME_FORMAT_STRING),
            "podID": record.podID,
            "swarm_name": record.swarm_name,
            "run_name": record.run_name,
            "loc_name": record.loc_name,
            "latitude": record.latitude,
            "longitude": record.longitude,
            "S2_taxonID_str": record.S2_taxonID_str,
            "S2_taxonID_score": record.S2_taxonID_score,
            "S2_taxonRank": record.S2_taxonRank,
            "S2a_score": record.S2a_score,
            "S1_class": record.S1_class,
        }
        if incl_images:
            record_dict["image"] = None  # Placeholder, add your image logic here
        timeline_data.append(record_dict)
    
    return timeline_data