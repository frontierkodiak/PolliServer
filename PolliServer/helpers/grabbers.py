# PolliOS/PolliServer/helpers/grabbers.py
import datetime
from sqlalchemy import and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
import traceback

from PolliServer.constants import *
from models.models import SpecimenRecord, PodRecord, FrameLog, WeatherRecord
from PolliServer.logger.logger import LoggerSingleton
from PolliServer.helpers.getters import get_frame_counts, get_recent_location

logger = LoggerSingleton().get_logger()


# NOTE: For @app.get("/frame-log-array-data") endpoint
async def grab_frame_log_array_data(db: AsyncSession, span: int, n_bins: int, swarm_name: Optional[str] = None, run_name: Optional[str] = None):
    # Convert span from hours to a timedelta
    span_delta = datetime.timedelta(hours=span)
    end_datetime = datetime.datetime.utcnow()
    start_datetime = end_datetime - span_delta

    # Calculate the time interval for each bin
    bin_interval = span_delta / n_bins

    # Initialize a list to hold the midpoint of each time bin
    bin_midpoints = [start_datetime + (i * bin_interval) + (bin_interval / 2) for i in range(n_bins)]

    # Query all unique podIDs within the span to pre-populate the structure
    pod_ids_query = select(FrameLog.podID).distinct()
    result = await db.execute(pod_ids_query)
    all_podIDs = [row[0] for row in result.all()]

    # Initialize a structure to hold the data for each podID for each time bin
    frame_log_dict = {podID: {bin_midpoint.strftime(DATETIME_FORMAT_STRING): 0 for bin_midpoint in bin_midpoints} for podID in all_podIDs}

    for i in range(n_bins):
        # Calculate the start and end time for the current bin
        bin_start_time = start_datetime + i * bin_interval
        bin_end_time = bin_start_time + bin_interval

        # Build the query to count frames and group by podID
        query = select(FrameLog.podID, func.count(FrameLog.id)).\
                filter(FrameLog.timestamp.between(bin_start_time, bin_end_time)).\
                group_by(FrameLog.podID)
                
                # FUTURE: Add filters for swarm_name and run_name, if provided

        # Execute the query
        result = await db.execute(query)
        frames_per_pod = result.all()

        # Update the structure with actual counts
        for podID, count in frames_per_pod:
            frame_log_dict[podID][bin_midpoints[i].strftime(DATETIME_FORMAT_STRING)] = count

    # Convert the dictionary to the list of objects expected by the frontend
    final_data = []
    for podID, bins in frame_log_dict.items():
        for bin_midpoint, count in bins.items():
            final_data.append({
                "time_bin_midpoint": bin_midpoint,
                "count": count,
                "podID": podID
            })

    # Sort final_data by time_bin_midpoint
    final_data_sorted = sorted(final_data, key=lambda x: datetime.datetime.strptime(x["time_bin_midpoint"], DATETIME_FORMAT_STRING))

    return final_data_sorted

# NOTE: For @app.get("/specimen-log-array-data") endpoint
async def grab_specimen_log_array_data(db: AsyncSession, span: int, n_bins: int, swarm_name: Optional[str] = None, run_name: Optional[str] = None):
    """
    Fetches specimen log data, aggregated into time bins, optionally filtered by swarm_name and/or run_name.
    
    Args:
        db (AsyncSession): Database session for executing queries.
        span (int): Time span in hours for which to fetch data.
        n_bins (int): Number of bins to divide the time span into.
        swarm_name (Optional[str]): Name of the swarm to filter by. Default is None.
        run_name (Optional[str]): Name of the run to filter by. Default is None.
    
    Returns:
        List[Dict]: A list of dictionaries, each representing a time bin with the following keys:
            - "time_bin_midpoint": The midpoint of the time bin, as a string in DATETIME_FORMAT_STRING format.
            - "count": The number of specimens recorded in this time bin.
            - "podID": The ID of the pod.
    
    This function mimics the structure and logic of grab_frame_log_array_data, but queries the SpecimenRecord table.
    """
    # Convert span from hours to a timedelta
    span_delta = datetime.timedelta(hours=span)
    end_datetime = datetime.datetime.utcnow()
    start_datetime = end_datetime - span_delta

    # Calculate the time interval for each bin
    bin_interval = span_delta / n_bins

    # Initialize a list to hold the midpoint of each time bin
    bin_midpoints = [start_datetime + (i * bin_interval) + (bin_interval / 2) for i in range(n_bins)]

    # Query all unique podIDs within the span to pre-populate the structure
    pod_ids_query = select(SpecimenRecord.podID).distinct()
    if swarm_name:
        pod_ids_query = pod_ids_query.filter(SpecimenRecord.swarm_name == swarm_name)
    if run_name:
        pod_ids_query = pod_ids_query.filter(SpecimenRecord.run_name == run_name)
    result = await db.execute(pod_ids_query)
    all_podIDs = [row[0] for row in result.all()]

    # Initialize a structure to hold the data for each podID for each time bin
    specimen_log_dict = {podID: {bin_midpoint.strftime(DATETIME_FORMAT_STRING): 0 for bin_midpoint in bin_midpoints} for podID in all_podIDs}

    for i in range(n_bins):
        # Calculate the start and end time for the current bin
        bin_start_time = start_datetime + i * bin_interval
        bin_end_time = bin_start_time + bin_interval

        # Build the query to count specimens and group by podID
        query = select(SpecimenRecord.podID, func.count(SpecimenRecord.id)).\
                filter(SpecimenRecord.timestamp.between(bin_start_time, bin_end_time))
        if swarm_name:
            query = query.filter(SpecimenRecord.swarm_name == swarm_name)
        if run_name:
            query = query.filter(SpecimenRecord.run_name == run_name)
        query = query.group_by(SpecimenRecord.podID)

        # Execute the query
        result = await db.execute(query)
        specimens_per_pod = result.all()

        # Update the structure with actual counts
        for podID, count in specimens_per_pod:
            specimen_log_dict[podID][bin_midpoints[i].strftime(DATETIME_FORMAT_STRING)] = count

    # Convert the dictionary to the list of objects expected by the frontend
    final_data = []
    for podID, bins in specimen_log_dict.items():
        for bin_midpoint, count in bins.items():
            final_data.append({
                "time_bin_midpoint": bin_midpoint,
                "count": count,
                "podID": podID
            })

    # Sort final_data by time_bin_midpoint
    final_data_sorted = sorted(final_data, key=lambda x: datetime.datetime.strptime(x["time_bin_midpoint"], DATETIME_FORMAT_STRING))

    return final_data_sorted

# NOTE: For @app.get("/weather-log-array-data") endpoint
async def grab_weather_log_array_data(db: AsyncSession, span: int, n_bins: int, swarm_name: Optional[str] = None, lite: bool = False):
    """
    Fetches weather log data, aggregated into time bins, optionally filtered by swarm_name.
    If 'lite' is True, only returns a subset of the weather data.

    Args:
        db (AsyncSession): Database session for executing queries.
        span (int): Time span in hours for which to fetch data.
        n_bins (int): Number of bins to divide the time span into.
        swarm_name (Optional[str]): Name of the swarm to filter by. Default is None.
        lite (bool): Whether to return a lite version of the data. Default is False.
    
    Returns:
        List[Dict]: A list of dictionaries, each representing a time bin with weather data.
    """
    span_delta = datetime.timedelta(hours=span)
    end_datetime = datetime.datetime.utcnow()
    start_datetime = end_datetime - span_delta
    bin_interval = span_delta / n_bins
    bin_midpoints = [start_datetime + (i * bin_interval) + (bin_interval / 2) for i in range(n_bins)]

    query = select(WeatherRecord).where(WeatherRecord.timestamp.between(start_datetime, end_datetime))
    if swarm_name:
        query = query.filter(WeatherRecord.swarm_name == swarm_name)
    
    result = await db.execute(query)
    weather_records = result.scalars().all()

    # Initialize a dictionary to hold the closest record to each bin midpoint
    closest_records = {}

    for bin_midpoint in bin_midpoints:
        closest_record = None
        smallest_diff = None
        for record in weather_records:
            current_diff = abs(record.timestamp - bin_midpoint)
            if closest_record is None or current_diff < smallest_diff:
                closest_record = record
                smallest_diff = current_diff
        if closest_record:
            data = {field: getattr(closest_record, field) for field in WeatherRecord.__table__.columns.keys() if getattr(closest_record, field) is not None}
            if lite:
                data = {k: v for k, v in data.items() if k in ["cloud_coverage", "wind_speed", "humidity", "temperature", "uv_index"]}
            closest_records[bin_midpoint.strftime(DATETIME_FORMAT_STRING)] = data

    final_data = [{"time_bin_midpoint": key, "data": value} for key, value in closest_records.items()]
    final_data_sorted = sorted(final_data, key=lambda x: datetime.datetime.strptime(x["time_bin_midpoint"], DATETIME_FORMAT_STRING))

    return final_data_sorted


async def grab_swarm_status(db: AsyncSession):
    '''
    Get swarm status from PodRecord MySQL database records.
    Returns JSON swarm_status list with the following object values:
        - podID
        - podOS_version
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
        stmt = select(PodRecord).filter(PodRecord.last_seen_time > cutoff_time)
        result = await db.execute(stmt)
        records = result.scalars().all()

        if not records:  # If there are no records, return a list with a single status object with all fields as None
            return [{
                'podID': None,
                'podOS_version': None,
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
            
            if record.last_seen_time:
                time_since_last_seen = datetime.datetime.utcnow() - record.last_seen_time
            else:
                time_since_last_seen = 0
            if record.last_specimen_created_time:
                time_since_last_specimen = datetime.datetime.utcnow() - record.last_specimen_created_time
            else:
                time_since_last_specimen = 0

            # Get the total frames for this podID using the get_frame_counts function
            total_frames_dict = await get_frame_counts(db, hours=24, podID=record.name, compare=False)
            total_frames = total_frames_dict['current']
            
            location = await get_recent_location(db, record.name)

            pod_status = {
                'podID': record.name,
                'podOS_version': record.pod_firmware_version,
                'pod_address': record.address,
                'connection_status': record.connection_status,
                'rssi': record.rssi,
                'stream_type': record.stream_type,
                'loc_name': record.location_name,
                'loc_lat': location['latitude'] if location else None,
                'loc_lon': location['longitude'] if location else None,
                'total_frames': total_frames, # total_frames, record.total_frames  # Use the total frames obtained from the get_frame_counts function
                'last_S1_class': record.last_S1_class,
                'last_S2_class': record.last_S2_class,
                'total_specimens': record.total_specimens,
                'last_specimen_created_time': record.last_specimen_created_time.strftime(DATETIME_FORMAT_STRING) if record.last_specimen_created_time else None,
                'last_seen': record.last_seen_time.strftime(DATETIME_FORMAT_STRING) if record.last_seen_time else None,
                'time_since_last_seen': time_since_last_seen.total_seconds() / 60.0 if record.last_seen_time else None,
                'time_since_last_specimen': time_since_last_specimen.total_seconds() / 60.0 if record.last_specimen_created_time else None
            }
            swarm_status.append(pod_status)  # Append each status object to the list

        return swarm_status
    except Exception as e:
        logger.server_error(f"Error in grab_swarm_status function: {e}")
        traceback.print_exc()  # This will print the traceback to the console.
        # Re-raise the exception so that the calling function can catch it
        raise e

# NOTE: for /specimen-detail-timeline endpoint
def build_specimen_detail_timeline_query(start_date=None, end_date=None, podID=None, location=None, 
                             S1_score_thresh=0.0, S2_score_thresh=0.0, S2a_score_thresh=0.0, species_only=False):

    # Subquery to get S2_taxonIDs that appear at least 5 times
    subquery = select(SpecimenRecord.S2_taxonID).group_by(SpecimenRecord.S2_taxonID).having(func.count(SpecimenRecord.S2_taxonID) >= 25)

    stmt = select(SpecimenRecord)

    conditions = []

    if start_date and end_date:
        start_datetime = datetime.datetime.strptime(start_date, DATE_FORMAT_STRING)
        end_datetime = datetime.datetime.strptime(end_date, DATE_FORMAT_STRING)
        conditions.append(SpecimenRecord.timestamp.between(start_datetime, end_datetime))
    
    if podID:
        conditions.append(SpecimenRecord.podID.in_(podID))
    
    if location:
        conditions.append(SpecimenRecord.loc_name == location)
    
    if S1_score_thresh > 0.0:
        conditions.append(SpecimenRecord.S1_score >= S1_score_thresh)
    
    if S2_score_thresh > 0.0:
        conditions.append(SpecimenRecord.S2_taxonID_score >= S2_score_thresh)
        
    if S2a_score_thresh > 0.0:
        conditions.append(SpecimenRecord.S2a_score >= S2a_score_thresh)
    
    if species_only:
        conditions.append(SpecimenRecord.S2_taxonRank == 'L10')

    # Add condition to filter S2_taxonID by subquery
    conditions.append(SpecimenRecord.S2_taxonID.in_(subquery))

    stmt = stmt.where(and_(*conditions))

    # Limiting the results as before
    stmt = stmt.limit(5000)
    
    return stmt

async def grab_specimen_detail_timeline(db: AsyncSession,
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None,
                             podID: Optional[List[str]] = None,
                             location: Optional[str] = None,
                             species_only: Optional[bool] = False,
                             S1_score_thresh: Optional[float] = 0.0,
                             S2_score_thresh: Optional[float] = 0.0,
                             S2a_score_thresh: Optional[float] = 0.0,
                             incl_images: Optional[bool] = False):

    records_query = build_specimen_detail_timeline_query(start_date, end_date, podID, location, 
                                              S1_score_thresh, S2_score_thresh, S2a_score_thresh, species_only)
    
    result = await db.execute(records_query)
    records = result.scalars().all()

    # DEV: image placeholder. Probably will not be implemented in this function
    if incl_images:
        pass

    specimen_detail_timeline = []
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
        specimen_detail_timeline.append(record_dict)
    
    return specimen_detail_timeline



async def grab_clade_activity_array_data(db: AsyncSession, clade: str, start_date: str, end_date: str, taxonRank: int, S1_score_thresh: float, S2_score_thresh: float, S2a_score_thresh: float, n_bins: int):
    # Convert start_date and end_date to datetime objects
    start_datetime = datetime.strptime(start_date, DATETIME_FORMAT_STRING)
    end_datetime = datetime.strptime(end_date, DATETIME_FORMAT_STRING)

    # Calculate the time difference between start_date and end_date
    time_diff = end_datetime - start_datetime

    # Calculate the time interval for each bin
    bin_interval = time_diff / n_bins

    # Initialize the array to store the results
    activity_array = []

    # Determine the taxonID_str column to use based on the clade
    if clade == 'Species':
        taxonID_str_column = SpecimenRecord.L10_taxonID_str
    elif clade == 'Genus':
        taxonID_str_column = SpecimenRecord.L20_taxonID_str
    # Add more elif statements for other clade values...

    # Loop over each bin
    for i in range(n_bins):
        # Calculate the start and end time for the current bin
        bin_start_time = start_datetime + i * bin_interval
        bin_end_time = bin_start_time + bin_interval

        # Build the query
        query = db.query(taxonID_str_column, func.count(taxonID_str_column)).filter(SpecimenRecord.timestamp.between(bin_start_time, bin_end_time))

        # Apply the score thresholds
        query = query.filter(SpecimenRecord.S1_score >= S1_score_thresh)
        query = query.filter(SpecimenRecord.S2_taxonID_score >= S2_score_thresh)
        query = query.filter(SpecimenRecord.S2a_score >= S2a_score_thresh)

        # Group by the taxonID_str column and order by the count
        query = query.group_by(taxonID_str_column).order_by(func.count(taxonID_str_column).desc())

        # Execute the query and get the results
        results = query.all()

        # Calculate the midpoint of the time bin
        bin_midpoint = bin_start_time + bin_interval / 2

        # Loop over the results and append a dictionary to the activity_array for each one
        for taxonID_str, count in results:
            activity_array.append({
                'time_bin_midpoint': bin_midpoint.strftime(DATETIME_FORMAT_STRING),
                'taxonID_str': taxonID_str,
                'count': count
            })

    return activity_array