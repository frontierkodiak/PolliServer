# PolliServer/helpers/getters.py
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import FrameLog, SensorRecord


async def get_frame_counts(db: AsyncSession, podID: str, hours: int = 24):
    # Calculate the datetime for <hours> ago
    hours_ago = datetime.utcnow() - timedelta(hours=hours)
    
    # Query the FrameLog table for the total number of frames for this podID within the past <hours>
    stmt = select(func.count()).where(and_(FrameLog.podID == podID, FrameLog.timestamp >= hours_ago))
    result = await db.execute(stmt)
    
    # Get the count from the result
    count = result.scalar_one()
    
    # Return the count
    return count


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