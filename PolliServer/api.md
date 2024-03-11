# PolliServer API Documentation

## Endpoints

### `/specimen-log-array-data`
Fetches aggregated specimen data over a specified time span, divided into bins, with optional filtering by swarm and run names.

- **Parameters**:
  - `span` (int, required): Time span in hours.
  - `n_bins` (int, optional, default=10): Number of bins.
  - `swarm_name` (str, optional): Swarm name filter.
  - `run_name` (str, optional): Run name filter.

- **Returns**: List of dictionaries with `time_bin_midpoint` (UTC), `count`, and `podID`.

- **Example Response**:
```json
[
    {
        "time_bin_midpoint": "2023-04-01T12:00:00",
        "count": 5,
        "podID": "Pod1"
    },
    {
        "time_bin_midpoint": "2023-04-01T13:00:00",
        "count": 8,
        "podID": "Pod1"
    }
]
```



### `/frame-log-array-data`
Fetches aggregated frame activity data over a specified time span, divided into bins, with optional filtering by swarm and run names.

- **Parameters**:
  - `span`, `n_bins`, `swarm_name`, `run_name` (same as above).

- **Returns**: List of dictionaries with `time_bin_midpoint` (UTC), `count`, and `podID`.

- **Example Response**:
```json
[
    {
        "time_bin_midpoint": "2023-04-01T12:00:00",
        "count": 10,
        "podID": "Pod2"
    },
    {
        "time_bin_midpoint": "2023-04-01T13:00:00",
        "count": 15,
        "podID": "Pod2"
    }
]
```

### `/weather-log-array-data`
Fetches aggregated weather data over a specified time span, divided into bins, with optional filtering by swarm name. Can return a full or lite dataset.

- **Parameters**:
  - `span`, `n_bins` (same as above).
  - `swarm_name` (str, optional): Swarm name filter.
  - `lite` (bool, optional): If true, returns a reduced set of weather data.

- **Returns**: 
  - Full: List of dictionaries with weather data for each time bin.
  - Lite: Reduced set including only `cloud_coverage`, `wind_speed`, `humidity`, `temperature`, and `uv_index`.

- **Example Response (Full)**:
json
[
{
"time_bin_midpoint": "2023-04-01T12:00:00",
"cloud_coverage": 75,
"rain_last_3h": 0.0,
"wind_degree": 180,
"wind_speed": 3.6,
"humidity": 65,
"pressure": 1012,
"temperature": 293.15,
"aqi": 25,
"coi": 0.1,
"nh3i": 0.01,
"noi": 0.02,
"no2i": 0.03,
"o3i": 0.04,
"so2i": 0.05,
"pm25i": 10, "pm10i": 20, "uv_index": 5.5 } ]

- **Example Response (Lite)**:
json [ { "time_bin_midoint": "2023-04-01T12:00:00", "cloud_coverage": 75, "wind_speed": 3.6, "humidity": 65, "temperature": 293.15, "uv_index": 5.5 } ]
