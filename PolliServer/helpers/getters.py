# PolliServer/helpers/getters.py
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import FrameLog, SensorRecord, SpecimenRecord


async def get_frame_counts(db: AsyncSession, hours: int = 24, podID: str = None, compare: bool = False):
    # Calculate the datetime for <hours> ago
    hours_ago = datetime.utcnow() - timedelta(hours=hours)

    # Define the base query
    base_query = select(func.count())

    # If podID is provided, add it to the filters
    if podID:
        base_query = base_query.where(FrameLog.podID == podID)

    # Query for the current period
    current_query = base_query.where(FrameLog.timestamp >= hours_ago)
    current_result = await db.execute(current_query)
    current_count = current_result.scalar_one()

    if compare:
        # Calculate the datetime for <hours> ago from the start of the current period
        previous_hours_ago = hours_ago - timedelta(hours=hours)

        # Query for the previous period
        previous_query = base_query.where(and_(FrameLog.timestamp >= previous_hours_ago, FrameLog.timestamp < hours_ago))
        previous_result = await db.execute(previous_query)
        previous_count = previous_result.scalar_one()

        # Return the counts for the current and previous periods, and the span
        return {'current': current_count, 'previous': previous_count, 'span': hours}

    # If not comparing, return the count for the current period and the span
    return {'current': current_count, 'span': hours}


async def get_specimen_counts(db: AsyncSession, hours: int, podID: str = None, swarm_name: str = None, compare: bool = False):
    # Calculate the datetime for <hours> ago
    hours_ago = datetime.utcnow() - timedelta(hours=hours)

    # Define the base query with the required filters
    base_query = select(func.count()).where(and_(
        SpecimenRecord.S1_score > 0.3,
        SpecimenRecord.S2_taxonID_score > 0.3,
        SpecimenRecord.bbox_rel_area > 0.005,
        SpecimenRecord.polli_mode == "swarm"
    ))

    # If podID is provided, add it to the filters
    if podID:
        base_query = base_query.where(SpecimenRecord.podID == podID)

    # If swarm_name is provided, add it to the filters
    if swarm_name:
        base_query = base_query.where(SpecimenRecord.swarm_name == swarm_name)

    # Query for the current period
    current_query = base_query.where(SpecimenRecord.timestamp >= hours_ago)
    current_result = await db.execute(current_query)
    current_count = current_result.scalar_one()

    if compare:
        # Calculate the datetime for <hours> ago from the start of the current period
        previous_hours_ago = hours_ago - timedelta(hours=hours)

        # Query for the previous period
        previous_query = base_query.where(and_(SpecimenRecord.timestamp >= previous_hours_ago, SpecimenRecord.timestamp < hours_ago))
        previous_result = await db.execute(previous_query)
        previous_count = previous_result.scalar_one()

        # Return the counts for the current and previous periods, and the span
        return {'current': current_count, 'previous': previous_count, 'span': hours}

    # If not comparing, return the count for the current period and the span
    return {'current': current_count, 'span': hours}

async def get_recent_location(db: AsyncSession, podID: str):
    # Query the SensorRecord table for the most recent record for this podID with non-empty latitude and longitude
    stmt = select(SensorRecord).where(and_(SensorRecord.podID == podID, SensorRecord.latitude.isnot(None), SensorRecord.longitude.isnot(None))).order_by(desc(SensorRecord.timestamp)).limit(1)
    result = await db.execute(stmt)

    # Get the record from the result
    record = result.scalar_one_or_none()

    # If a record was found, return the latitude and longitude
    if record:
        return {'latitude': record.latitude, 'longitude': record.longitude}

    # If no record was found, return None
    return None