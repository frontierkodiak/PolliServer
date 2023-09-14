# PolliServer.server.py

from typing import Optional, List
from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import func
import traceback


from PolliServer.constants import *
from PolliServer.backend.get_db import get_db
from PolliServer.helpers.grabbers import *
from models.models import SpecimenRecord
from PolliServer.logger.logger import LoggerSingleton

logger = LoggerSingleton().get_logger()


app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Minor (getter) API endpoints --- #

# Async endpoint to serve the favicon.ico file
@app.get("/favicon.ico")
async def get_favicon():
    '''
    Returns:
        FileResponse: Favicon file to be served
    '''
    return FileResponse("assets/favicons/Polli_Dandelion_v1.0_trans.png")

@app.get("/podIDs")
async def get_pod_ids(db: AsyncSession = Depends(get_db)):
    try:
        values = await db.execute(select(SpecimenRecord.podID).distinct())
        values_list = [item[0] for item in values.scalars().all()]
        return sorted(values_list)
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /pod_ids SQLAlchemyError: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/locations")
async def get_locations(db: AsyncSession = Depends(get_db)):
    try:
        values = await db.execute(select(SpecimenRecord.loc_name).distinct())
        values_list = [item[0] for item in values.scalars().all()]
        return sorted(values_list)
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /locations SQLAlchemyError: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/swarms")
async def get_swarms(db: AsyncSession = Depends(get_db)):
    try:
        values = await db.execute(select(SpecimenRecord.swarm_name).distinct())
        values_list = [item[0] for item in values.scalars().all()]
        return sorted(values_list)
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /swarms SQLAlchemyError: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/runs")
async def get_runs(db: AsyncSession = Depends(get_db)):
    try:
        values = await db.execute(select(SpecimenRecord.run_name).distinct())
        values_list = [item[0] for item in values.scalars().all()]
        return sorted(values_list)
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /runs SQLAlchemyError: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dates")
async def get_dates(db: AsyncSession = Depends(get_db)):
    try:
        # Extract distinct dates (ignoring time)
        dates = await db.execute(select(func.date(SpecimenRecord.timestamp)).distinct())
        # Convert datetime.date objects to string and sort them
        dates_list = sorted([date_obj[0].strftime('%Y-%m-%d') for date_obj in dates.scalars().all()])
        return dates_list
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /dates SQLAlchemyError: {e}")
        raise HTTPException(status_code=500, detail=str(e))


        
# --- Major (grabber) API endpoints --- #

# Returns a swarm_status JSON swarm_status list
@app.get("/api/swarm-status")
async def swarm_status(db: AsyncSession = Depends(get_db)):
    try:
        return await grab_swarm_status(db)
    except Exception as e:
        logger.server_error(f"Error in swarm_status endpoint: {e}")
        traceback.print_exc()  # This will print the traceback to the console.
        raise HTTPException(status_code=500, detail="Internal server error")


# Returns a timeline_data JSON dict (no keys)
@app.get("/api/timeline-data")
async def timeline_data(start_date: Optional[str] = Query(None),
                  end_date: Optional[str] = Query(None),
                  podID: Optional[List[str]] = Query(None),
                  species_only: Optional[bool] = Query(False),
                  S1_score_thresh: Optional[float] = Query(0.0),
                  S2_score_thresh: Optional[float] = Query(0.0),
                  location: Optional[str] = Query(None),
                  S2a_score_thresh: Optional[float] = Query(0.0),
                  incl_images: Optional[bool] = Query(False),
                  ):
    
    timeline_data = grab_timeline_data(start_date = start_date, end_date=end_date, podID=podID, 
                                       location=location, species_only=species_only, 
                                       S1_score_thresh=S1_score_thresh, S2_score_thresh=S2_score_thresh, 
                                       S2a_score_thresh=S2a_score_thresh, incl_images=incl_images)
    
    return timeline_data