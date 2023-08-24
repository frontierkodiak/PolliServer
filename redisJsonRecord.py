import datetime
from typing import Optional, Union
from redis import Redis
import warnings


from redis_om import (
    EmbeddedJsonModel,
    JsonModel,
    Field,
    Migrator,
    HashModel)

import logging.config
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})


class PodRecord(JsonModel):
    '''
    Sister to GlobalPods Pod objects. Updated when GlobalPods are updated.
    Stores ephemeral data about the Pod. Last readings, detections, etc.
    '''
    
    #### Basic Pod info
    name: Optional[str] = Field(index=True)
    address: Optional[str]
    address_type: Optional[str]
    swarm_name: Optional[str] = Field(index=True)
    retry_connection_period: Optional[int]
    
    ### Stream params
    stream_type: Optional[str]
    downsample_fps: Optional[int]
    connection_type: Optional[str]
    rtsp_port: Optional[int]
    buffer_size: Optional[int]
    stream_address: Optional[str]
    snapshot_address: Optional[str]
    snapshot_interval: Optional[int]
    
    ### Pod status
    connection_status: Optional[str]
    last_seen: Optional[datetime.datetime]
    queue_length: Optional[int]
    total_frames: Optional[int]
    last_L1_class: Optional[str]
    last_L2_class: Optional[str]
    last_N_L1_classes: Optional[list]
    last_N_L2_classes: Optional[list]
    total_specimens: Optional[int]
    last_specimen_created_time: Optional[datetime.datetime]
    
    ##### PodOS advanced features (0.4.x+)
    #### PodOS endpoints
    get_config_endpoint: Optional[str]
    restart_endpoint: Optional[str]
    get_sensor_status_endpoint: Optional[str]
    sensors_endpoint: Optional[str]
    update_GPS_endpoint: Optional[str]
    naptime_endpoint: Optional[str]
    bedtime_endpoint: Optional[str]
    shutdown_GPS_endpoint: Optional[str]
    wakeup_GPS_endpoint: Optional[str]
    
    ### Update intervals
    get_config_interval: Optional[int]
    get_sensor_status_interval: Optional[int]
    get_sensors_interval: Optional[int]
    get_update_GPS_before_init_fix_interval: Optional[int]
    snapshot_interval: Optional[float] # float, as it can be a fraction of a second.
    
    #### PodOS sensors
    ### Sensor status
    camera_available: Optional[bool]
    bme280_available: Optional[bool]
    gps_available: Optional[bool]
    gps_awake: Optional[bool]
    battery_reader_available: Optional[bool]
    
    ### Sensor config
    bme280_scl_pin: Optional[int]
    bme280_sda_pin: Optional[int]
    gps_rx_pin: Optional[int]
    gps_tx_pin: Optional[int]
    gps_pwrctl_available: Optional[bool]
    gps_pwrctl_pin: Optional[int]
    battery_reader_pin: Optional[int]
    jpg_quality: Optional[int]
    
    ### Sensor data
    location_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    altitude: Optional[float]
    temperature: Optional[float]
    pressure: Optional[float]
    humidity: Optional[float]
    battery_level: Optional[float]
    rssi: Optional[int]
    
    #### PodOS management
    ### Naptime
    naptime_enabled: Optional[bool]
    naptime_baseline: Optional[int]
    
    ### Bedtime
    bedtime_active: Optional[bool]
    bedtime_max_wait: Optional[int]
    bedtime_start: Optional[datetime.datetime]
    bedtime_end: Optional[datetime.datetime]
    
    #### PodOS metadata
    pod_name: Optional[str]
    firmware_name: Optional[str]
    firmware_version: Optional[str]


class L1Card(EmbeddedJsonModel):
    '''
    Records details about the module producing some SpecimenRecord or EventRecord.
    '''
    tag: Optional[str] = Field(index=True)
    vers: Optional[str]
    classification: Optional[str]
    score: Optional[float]

class L2Card(EmbeddedJsonModel):
    '''
    Records details about the module producing some SpecimenRecord or EventRecord.
    '''
    tag: Optional[str] = Field(index=True)
    vers: Optional[str]
    classification: Optional[str]
    taxonID: Optional[str] = Field(index=True) # DEV: Might refactor relationship b/w L2Card and Taxa.
    score: Optional[float]

class L3Card(EmbeddedJsonModel):
    '''
    Records details about the module producing some SpecimenRecord or EventRecord.
    '''
    tag: Optional[str] = Field(index=True)
    vers: Optional[str]
    classification: Optional[str]
    score: Optional[float]

class Taxa(EmbeddedJsonModel):
    '''
    Records taxonomic information about the specimen.
    '''
    taxonID: Optional[str] = Field(index=True) # Placeholder. This key will be used to reference master taxon table.
    taxonID_str: Optional[str] = Field(index=True)
    taxonID_score: Optional[float] = Field(index=True)
    taxonRank: Optional[str] = Field(index=True) # Lowest taxonomic rank for which a classification was made.
    L10_taxonID: Optional[str] = Field(index=True)
    L10_taxonID_str: Optional[str]
    L10_taxonScore: Optional[float]
    L20_taxonID: Optional[str] = Field(index=True)
    L20_taxonID_str: Optional[str]
    L20_taxonScore: Optional[float]
    L30_taxonID: Optional[str] = Field(index=True)
    L30_taxonID_str: Optional[str]
    L30_taxonScore: Optional[float]
    L40_taxonID: Optional[str] = Field(index=True)
    L40_taxonID_str: Optional[str]
    L40_taxonScore: Optional[float]
    L50_taxonID: Optional[str] = Field(index=True)
    L50_taxonID_str: Optional[str]
    L50_taxonScore: Optional[float]

class Media(EmbeddedJsonModel):
    '''
    Records media details for a specimen. CLARIFY: Not sure if I want to refactor this info from FrameRecord right now.
    '''
    mediaID: Optional[str]
    mediaType: Optional[str]
    height_px: Optional[int]
    width_px: Optional[int]
    persist_policy: Optional[str] # Would need to be set by module creating this record.

class Frame(EmbeddedJsonModel):
    '''
    '''
    timestamp: Optional[datetime.datetime] = Field(index=True)
    run_name: Optional[str] = Field(index=True) 
    podID: Optional[str] = Field(index=True)
    swarm_name: Optional[str] = Field(index=True)

class Location(EmbeddedJsonModel):
    lat: Optional[float]
    lon: Optional[float]
    loc_name: Optional[str]

class Detection(EmbeddedJsonModel):
    '''
    Only used when creating from L1 module results.
    '''
    classification: Optional[str]
    bboxLL: Optional[tuple]
    bboxUR: Optional[tuple]
    score: Optional[float]



class FrameRecord(JsonModel):
    '''
    FrameRecord is an ephemeral record created when a frame is received by the HubOS engine.
    Its properties are used to populate other records created by the engine.
    '''
    media: Media
    frame: Frame
    location: Location
    processed: Optional[bool] = Field(index=True) # DEV: Has frame been processed by engine? Used when merging FrameRecords from PolliOS Lite (offline mode, on Hub).
    
class SpecimenRecord(JsonModel):
    taxa: Taxa
    L1Card: Optional[L1Card]
    L2Card: Optional[L2Card]
    L3Card: Optional[L3Card]
    media: Media
    frame: Frame
    location: Optional[Location]
    detection: Detection

    # class Config:
    #     extra = "forbid"


class ImageRecord(HashModel):
    image: bytes
    # class Meta:
    #     database = Redis(db = 1, decode_responses=False)


class MetaModel(JsonModel):
    foo: Optional[str]

Migrator().run()
