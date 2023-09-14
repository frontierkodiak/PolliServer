# PolliOS.PolliServer.server.py

from typing import Optional, List
from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import func
import datetime
import traceback


from PolliOS.PolliServer.constants import *
from PolliOS.PolliServer.helpers.grabbers import *
from PolliOS.backend.models.models import SpecimenRecord
from PolliOS.logger import LoggerSingleton

logger = LoggerSingleton().get_logger()


app = FastAPI(debug=True)

origins = [
    "http://localhost:3000",  # React app address
    "http://localhost:3005",
    "http://localhost:3001",
    "http://calebs-ipad:3000",
    "http://calebs-ipad:3005",
    "http://blade:3000",
    "http://blade:3005",
    "http://pop-xps:3000",
    "http://pop-xps:3005",
    "http://pop-yoga:3000",
    "http://pop-yoga:3005",
    "http://r5-win:3000",
    "http://r5-win:3005",
    "http://my-infos-s10:3000",
    "http://my-infos-s10:3005",
    "http://hub0:3000",
    "http://hub0:3005",
    "http://100.126.14.72:3000",
    "http://100.126.14.72:3005",
    "http://100.118.87.109:3000",
    "http://100.118.87.109:3005",
    "http://100.66.70.13:3000",
    "http://100.66.70.13:3005",
    "http://100.87.193.56:3000",
    "http://100.87.193.56:3005",
    "http://100.119.21.33:3000",
    "http://100.119.21.33:3005",
    "http://100.67.247.68:3000",
    "http://100.67.247.68:3005",
    "http://100.114.217.98:3000",
    "http://100.114.217.98:3005",
    "http://192.168.1.47:3000",
    "http://192.168.1.47:3005"
]

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

# Endpoint to return all species names
@app.get("/L10_taxonID_strs")
async def get_L10_taxonID_strs(db: Session = Depends(get_db)):
    try:
        values = db.query(SpecimenRecord.L10_taxonID_str).distinct().all()
        values_list = [item[0] for item in values]
        return sorted(values_list)
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /L10_taxonID_strs SQLAlchemyError: {e}")
        return HTTPException(status_code=500, detail=str(e))

@app.get("/pod_ids")
async def get_pod_ids(db: Session = Depends(get_db)):
    try:
        values = db.query(SpecimenRecord.podID).distinct().all()
        values_list = [item[0] for item in values]
        return sorted(values_list)
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /pod_ids SQLAlchemyError: {e}")
        return HTTPException(status_code=500, detail=str(e))

@app.get("/locations")
async def get_locations(db: Session = Depends(get_db)):
    try:
        values = db.query(SpecimenRecord.loc_name).distinct().all()
        values_list = [item[0] for item in values]
        return sorted(values_list)
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /locations SQLAlchemyError: {e}")
        return HTTPException(status_code=500, detail=str(e))

@app.get("/swarms")
async def get_swarms(db: Session = Depends(get_db)):
    try:
        values = db.query(SpecimenRecord.swarm_name).distinct().all()
        values_list = [item[0] for item in values]
        return sorted(values_list)
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /swarms SQLAlchemyError: {e}")
        return HTTPException(status_code=500, detail=str(e))

@app.get("/runs")
async def get_runs(db: Session = Depends(get_db)):
    try:
        values = db.query(SpecimenRecord.run_name).distinct().all()
        values_list = [item[0] for item in values]
        return sorted(values_list)
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /runs SQLAlchemyError: {e}")
        return HTTPException(status_code=500, detail=str(e))

# Returns a sorted list of all valid dates
@app.get("/dates")
async def get_dates(db: Session = Depends(get_db)):
    try:
        # Extract distinct dates (ignoring time)
        dates = db.query(func.date(SpecimenRecord.timestamp)).distinct().all()
        
        # Convert datetime.date objects to string and sort them
        dates_list = sorted([date_obj[0].strftime('%Y-%m-%d') for date_obj in dates])
        return dates_list
    except SQLAlchemyError as e:
        logger.server_error(f"Getter /dates SQLAlchemyError: {e}")
        return HTTPException(status_code=500, detail=str(e))

        
# --- Major (grabber) API endpoints --- #

# Returns a swarm_status JSON swarm_status list
@app.get("/api/swarm-status")
async def swarm_status(db: Session = Depends(get_db)):
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
                  pod_id: Optional[List[str]] = Query(None),
                  species_only: Optional[bool] = Query(False),
                  L1_conf_thresh: Optional[float] = Query(0.0),
                  L2_conf_thresh: Optional[float] = Query(0.0),
                  location: Optional[str] = Query(None),
                  incl_images: Optional[bool] = Query(False)):
    
    timeline_data = grab_timeline_data(start_date = start_date, end_date=end_date, pod_id=pod_id, 
                                       location=location, species_only=species_only, 
                                       L1_conf_thresh=L1_conf_thresh, L2_conf_thresh=L2_conf_thresh, 
                                       incl_images=incl_images)
    
    return timeline_data