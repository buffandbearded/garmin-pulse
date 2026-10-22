select
    calendar_date,
    (payload->>'restingHeartRate')::numeric as resting_hr,
    (payload->>'minHeartRate')::numeric     as min_hr,
    (payload->>'maxHeartRate')::numeric     as max_hr,
    ingested_at
from {{ source('raw', 'garmin_heart_rate') }}
