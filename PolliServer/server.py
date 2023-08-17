from typing import Optional, List
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import datetime
import traceback


from PolliServer.constants import DATETIME_FORMAT_STRING, redis, redis_img, THUMBNAIL_SIZE
from PolliServer.helpers.grabbers import *
from PolliServer.helpers.getters import *

from redisJsonRecord import *

app = FastAPI(debug=True)
origins = [
    "http://localhost:3000",  # React app address
    "http://calebs-ipad:3000",
    "http://blade:3000",
    "http://pop-xps:3000",
    "http://pop-yoga:3000",
    "http://r5-win:3000",
    "http://my-infos-s10:3000",
    "http://hub0:3000",
    "http://100.126.14.72:3000",
    "http://100.118.87.109:3000",
    "http://100.66.70.13:3000",
    "http://100.87.193.56:3000",
    "http://100.119.21.33:3000",
    "http://100.67.247.68:3000",
    "http://100.114.217.98:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_helper = RedisJsonHelper(redis)

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
async def get_L10_taxonID_strs():
    try:
        taxon_strs = await redis_helper.L10_taxonID_strs_getter()
        return taxon_strs
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

# Returns a sorted list of all pod_ids
@app.get("/pod_ids")
async def get_pod_ids():
    try:
        pod_ids = await redis_helper.pod_ids_getter()
        return pod_ids
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

# Returns a sorted list of all location names
@app.get("/locations")
async def get_locations():
    try:
        locations = await redis_helper.locations_getter()
        return locations
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

# Returns a sorted list of all swarm names
@app.get("/swarms")
async def get_swarms():
    try:
        swarms = await redis_helper.swarms_getter()
        return swarms
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

# Returns a sorted list of all run names
@app.get("/runs")
async def get_runs():
    try:
        runs = await redis_helper.runs_getter()
        return runs
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

# Returns a sorted list of all valid dates
@app.get("/dates")
async def get_dates():
    try:
        dates = await redis_helper.dates_getter()
        return dates
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

        
# --- Major (grabber) API endpoints --- #

# Returns a swarm_status JSON swarm_status list
@app.get("/api/swarm-status")
async def swarm_status():
    swarm_status = await grab_swarm_status()
    return swarm_status

# Returns a timeline_data JSON dict (no keys)
@app.get("/api/timeline-data")
async def timeline_data(start_date: Optional[str] = Query(None),
                  end_date: Optional[str] = Query(None),
                  pod_id: Optional[List[str]] = Query(None),  # List[str] instead of str
                  species_only: Optional[bool] = Query(False),
                  L1_conf_thresh: Optional[float] = Query(0.0),
                  L2_conf_thresh: Optional[float] = Query(0.0),
                  location: Optional[str] = Query(None),
                  incl_images: Optional[bool] = Query(False)):
    timeline_data = await grab_timeline_data(start_date = start_date, end_date=end_date, pod_id=pod_id, 
                                             location=location, species_only=species_only, L1_conf_thresh=L1_conf_thresh, 
                                             L2_conf_thresh=L2_conf_thresh, incl_images=incl_images)
    return timeline_data