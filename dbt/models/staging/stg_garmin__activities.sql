select
    activity_id,
    start_time_local,
    payload->>'activityName'                      as activity_name,
    payload->'activityType'->>'typeKey'           as activity_type,
    (payload->>'duration')::numeric               as duration_s,
    (payload->>'distance')::numeric               as distance_m,
    (payload->>'calories')::numeric               as calories,
    (payload->>'averageHR')::numeric              as avg_hr,
    (payload->>'maxHR')::numeric                  as max_hr,
    (payload->>'elevationGain')::numeric          as elevation_gain_m,
    ingested_at
from {{ source('raw', 'garmin_activities') }}
