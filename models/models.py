# PolliOS.backend.models.models.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class PodRecord(Base):
    __tablename__ = 'pod_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), index=True)
    # type = Column(String(64), index=True)
    address = Column(String(64), index=True)
    address_type = Column(String(64))
    swarm_name = Column(String(64), index=True)
    retry_connection_period = Column(Integer)
    
    # Stream params
    stream_type = Column(String(64))
    downsample_fps = Column(Integer)
    connection_type = Column(String(64))
    rtsp_port = Column(Integer)
    buffer_size = Column(Integer)
    stream_address = Column(String(64))
    snapshot_address = Column(String(64))
    get_snapshot_interval = Column(Float)
    
    # Pod status
    connection_status = Column(String(64), index=True)
    last_seen = Column(DateTime)
    queue_length = Column(Integer)
    total_frames = Column(Integer)
    last_S1_class = Column(String(64))
    last_S2_class = Column(String(64))
    # last_N_S1_classes = Column(String(1024))  # Stored as comma-separated string. Consider using a related table.
    # last_N_S2_classes = Column(String(1024))  # Stored as comma-separated string. Consider using a related table.
    total_specimens = Column(Integer)
    last_specimen_created_time = Column(DateTime)
    
    # PodOS advanced features (0.4.x+)
    get_config_endpoint = Column(String(64))
    restart_endpoint = Column(String(64))
    get_sensor_status_endpoint = Column(String(64))
    sensors_endpoint = Column(String(64))
    update_GPS_endpoint = Column(String(64))
    naptime_endpoint = Column(String(64))
    bedtime_endpoint = Column(String(64))
    shutdown_GPS_endpoint = Column(String(64))
    wakeup_GPS_endpoint = Column(String(64))
    
    # Update intervals
    get_config_interval = Column(Integer)
    get_sensor_status_interval = Column(Integer)
    get_sensors_interval = Column(Integer)
    get_update_GPS_interval = Column(Integer)
    get_snapshot_interval = Column(Float)
    
    # PodOS sensors
    camera_available = Column(Boolean)
    bme280_available = Column(Boolean)
    gps_available = Column(Boolean)
    gps_awake = Column(Boolean)
    battery_reader_available = Column(Boolean)
    
    # Sensor config
    bme280_scl_pin = Column(Integer)
    bme280_sda_pin = Column(Integer)
    gps_rx_pin = Column(Integer)
    gps_tx_pin = Column(Integer)
    gps_pwrctl_available = Column(Boolean)
    gps_pwrctl_pin = Column(Integer)
    battery_reader_pin = Column(Integer)
    jpg_quality = Column(Integer)
    
    # Sensor data
    location_name = Column(String(64), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    temperature = Column(Float)
    pressure = Column(Float)
    humidity = Column(Float)
    battery_level = Column(Float)
    rssi = Column(Integer)
    
    # PodOS management
    naptime_enabled = Column(Boolean)
    naptime_baseline = Column(Integer)
    bedtime_active = Column(Boolean, index=True)
    bedtime_enabled = Column(Boolean, index=True)
    bedtime_max_wait = Column(Integer)
    bedtime_start = Column(DateTime)
    bedtime_end = Column(DateTime)
    
    # PodOS metadata
    pod_name = Column(String(64), index=True)
    pod_firmware_name = Column(String(64))
    pod_firmware_version = Column(String(64))

    
class SpecimenRecord(Base):
    __tablename__ = 'specimen_record'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    ## Stage 1 (detection)
    bboxLL_x = Column(Integer)
    bboxLL_y = Column(Integer)
    bboxUR_x = Column(Integer)
    bboxUR_y = Column(Integer)
    bbox_rel_area = Column(Float, index=True)
    S1_score = Column(Float, index=True)
    S1_tag = Column(String(64), index=True)
    S1_class = Column(String(255), index=True)

    ## Stage 2: (classification)
    S2_tag = Column(String(64), index=True)
    S2_taxonID = Column(String(64), index=True)
    S2_taxonID_str = Column(String(255), index=True)
    S2_taxonID_common_str = Column(String(255), index=True)
    S2_taxonID_score = Column(Float, index=True)
    S2_taxonRank = Column(String(64), index=True)
    
    ## Taxa
    L10_taxonID = Column(String(64), index=True)
    L10_taxonID_str = Column(String(255), index=True)
    L10_taxonScore = Column(Float, index=True)
    
    L20_taxonID = Column(String(64), index=True)
    L20_taxonID_str = Column(String(255))
    L20_taxonScore = Column(Float, index=True)
    
    L30_taxonID = Column(String(64), index=True)
    L30_taxonID_str = Column(String(255))
    L30_taxonScore = Column(Float, index=True)
    
    L40_taxonID = Column(String(64), index=True)
    L40_taxonID_str = Column(String(255))
    L40_taxonScore = Column(Float)
    
    L50_taxonID = Column(String(64), index=True)
    L50_taxonID_str = Column(String(255))
    L50_taxonScore = Column(Float, index=True)
    
    ## Plausibility / anomaly detection
    S2a_score = Column(Float, index=True)
    S2a_tag = Column(String(64), index=True)
    
    ## Task details
    target = Column(String(64), index=True)
    polli_mode = Column(String(64), index=True)
    
    ## Media
    mediaID = Column(String(255), index=True)
    mediaPath = Column(String(255))
    mediaType = Column(String(64))
    height_px = Column(Integer)
    width_px = Column(Integer)
    media_persist_policy = Column(String(64))
    
    ## Frame    
    timestamp = Column(DateTime, index=True)
    run_name = Column(String(64), index=True)
    podID = Column(String(64), index=True)
    swarm_name = Column(String(64), index=True)
    
    ## Location
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    loc_name = Column(String(64), index=True)
    
    ## PolliOS metadata
    polliOS_version = Column(String(64))
    
    # Sensor metadata
    sensorRecord_id = Column(Integer) # FUTURE: Associate specimen with sensor record.


class FrameRecord(Base):
    # NOTE: These are only used in PolliOS Lite. 
    # Base PolliOS sticks to pure python FrameCard objects.
    __tablename__ = 'frame_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mediaID = Column(String(255), index=True)
    mediaType = Column(String(64))
    target = Column(String(64), index=True)
    polli_mode = Column(String(64), index=True)
    height_px = Column(Integer)
    width_px = Column(Integer)
    persist_policy = Column(String(64))
    timestamp = Column(DateTime, index=True)
    run_name = Column(String(64), index=True)
    podID = Column(String(64), index=True)
    swarm_name = Column(String(64), index=True)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    loc_name = Column(String(64), index=True)
    synced = Column(Boolean, index=True)
    processed = Column(Boolean, index=True)
    queued = Column(Boolean, index=True)

class SensorRecord(Base):
    __tablename__ = 'sensor_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, index=True)
    podID = Column(String(64), index=True)
    # GPS
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    # BME280
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    # Battery
    battery_level = Column(Float)
    # RSSI
    rssi = Column(Float)

class FrameLog(Base):
    __tablename__ = 'frame_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, index=True)
    podID = Column(String(64), index=True)
    
class PollinationRecord(Base):
    __tablename__ = 'pollination_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, index=True)
    run_name = Column(String(64), index=True)
    swarm_name = Column(String(64), index=True)
    polli_mode = Column(String(64), index=True)
    
    # Event model meta
    S3_tag = Column(String(64), index=True)
    # Pipeline (Brain) meta
    brain_tag = Column(String(64), index=True)
    brain_arch = Column(String(64), index=True)
    brain_event_descriptor = Column(String(64), index=True)
    brain_type = Column(String(64))
    
    # Event details
    joint_bbox_overlap = Column(Float, index=True)
    
    # Specimen details
    ## Poll
    specimen_record_id_poll = Column(Integer, ForeignKey('specimen_record.id'))
    S2_taxonID_poll = Column(String(64), index=True) # These are supposed to be int. FUTURE: Reformat these in MySQL, inc. for SpecimenRecord.
    S2_taxonID_str_poll = Column(String(255), index=True)
    S2_taxonID_score_poll = Column(Float, index=True)
    S2_taxonRank_poll = Column(String(64), index=True) # Also supposed to be int.
    L10_taxonID_str_poll = Column(String(255))
    L20_taxonID_str_poll = Column(String(255))
    L30_taxonID_str_poll = Column(String(255))
    L40_taxonID_str_poll = Column(String(255))
    ## Plant
    specimen_record_id_plant = Column(Integer, ForeignKey('specimen_record.id'))
    S2_taxonID_plant = Column(String(64), index=True)
    S2_taxonID_str_plant = Column(String(255), index=True)
    S2_taxonID_score_plant = Column(Float, index=True)
    S2_taxonRank_plant = Column(String(64), index=True)
    L10_taxonID_str_plant = Column(String(255))
    L20_taxonID_str_plant = Column(String(255))
    L30_taxonID_str_plant = Column(String(255))
    L40_taxonID_str_plant = Column(String(255))
    
class WeatherRecord(Base):
    __tablename__ = 'weather_records'

    id = Column(Integer, primary_key=True)
    swarm_name = Column(String(64), index=True)
    run_name = Column(String(64), index=True)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    owm_city_id = Column(Integer, index=True)
    loc_name = Column(String(128), index=True)
    timestamp = Column(DateTime, index=True)
    cloud_coverage = Column(Integer)
    rain_last_3h = Column(Float)
    wind_degree = Column(Float)
    wind_speed = Column(Float)
    # wind_gust = Column(Float) # New. Non-OWM.
    humidity = Column(Integer)
    # par_light = Column(Float) # New. Non-OWM. uM/m^2s
    pressure = Column(Integer)
    temperature = Column(Float)
    snow_last_3h = Column(Float)
    sunrise_time = Column(DateTime)
    sunset_time = Column(DateTime)
    status = Column(String(64))
    detailed_status = Column(String(255))
    owm_code = Column(String(64))
    owm_icon_name = Column(String(64))
    owm_icon_url = Column(String(255))