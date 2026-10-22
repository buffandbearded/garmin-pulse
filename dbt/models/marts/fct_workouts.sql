select
    activity_id,
    start_time_local,
    start_time_local::date                 as calendar_date,
    activity_name,
    activity_type,
    round(duration_s / 60.0, 1)            as duration_min,
    round(distance_m / 1000.0, 2)          as distance_km,
    calories,
    avg_hr,
    max_hr,
    elevation_gain_m
from {{ ref('stg_garmin__activities') }}
