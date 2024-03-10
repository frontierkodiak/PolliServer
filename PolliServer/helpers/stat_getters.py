from datetime import datetime, timedelta
from typing import Dict, Optional, List
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import FrameLog, SensorRecord, SpecimenRecord


# NOTE: For /frame-log-stats endpoint
async def get_frame_log_stats(db: AsyncSession, span: int, swarm_name: Optional[str] = None, run_name: Optional[str] = None):
    # Calculate the datetime for <span> hours ago
    span_ago = datetime.utcnow() - timedelta(hours=span)

    # Define the base query
    base_query = select(func.count()).select_from(FrameLog)

    # Future implementation: Filter by swarm_name and run_name if provided
    # if swarm_name:
    #     base_query = base_query.where(FrameLog.swarm_name == swarm_name)
    # if run_name:
    #     base_query = base_query.where(FrameLog.run_name == run_name)

    # Query for the current period
    current_query = base_query.where(FrameLog.timestamp >= span_ago)
    current_result = await db.execute(current_query)
    current_count = current_result.scalar_one()

    # Calculate the datetime for <span> hours ago from the start of the current period
    previous_span_ago = span_ago - timedelta(hours=span)

    # Query for the previous period
    previous_query = base_query.where(and_(FrameLog.timestamp >= previous_span_ago, FrameLog.timestamp < span_ago))
    previous_result = await db.execute(previous_query)
    previous_count = previous_result.scalar_one()

    # Calculate the percent difference
    diff = ((current_count - previous_count) / previous_count) * 100 if previous_count else 0

    # Return the counts for the current and previous periods, and the percent difference
    return {'current': current_count, 'previous': previous_count, 'change': diff}


# NOTE: For /specimen-log-stats endpoint
async def get_specimen_log_stats(db: AsyncSession, span: int, swarm_name: Optional[str] = None, run_name: Optional[str] = None):
    # Calculate the datetime for <span> hours ago
    span_ago = datetime.utcnow() - timedelta(hours=span)

    # Define the base query
    base_query = select(func.count()).select_from(SpecimenRecord)

    # Future implementation: Filter by swarm_name and run_name if provided
    # if swarm_name:
    #     base_query = base_query.where(SpecimenRecord.swarm_name == swarm_name)
    # if run_name:
    #     base_query = base_query.where(SpecimenRecord.run_name == run_name)

    # Query for the current period
    current_query = base_query.where(SpecimenRecord.timestamp >= span_ago)
    current_result = await db.execute(current_query)
    current_count = current_result.scalar_one()

    # Calculate the datetime for <span> hours ago from the start of the current period
    previous_span_ago = span_ago - timedelta(hours=span)

    # Query for the previous period
    previous_query = base_query.where(and_(SpecimenRecord.timestamp >= previous_span_ago, SpecimenRecord.timestamp < span_ago))
    previous_result = await db.execute(previous_query)
    previous_count = previous_result.scalar_one()

    # Calculate the percent difference
    diff = ((current_count - previous_count) / previous_count) * 100 if previous_count else 0

    # Return the counts for the current and previous periods, and the percent difference
    return {'current': current_count, 'previous': previous_count, 'change': diff}