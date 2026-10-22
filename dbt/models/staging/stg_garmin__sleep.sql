select
    calendar_date,
    (payload->'dailySleepDTO'->>'sleepTimeSeconds')::numeric      as sleep_seconds,
    (payload->'dailySleepDTO'->>'deepSleepSeconds')::numeric      as deep_seconds,
    (payload->'dailySleepDTO'->>'lightSleepSeconds')::numeric     as light_seconds,
    (payload->'dailySleepDTO'->>'remSleepSeconds')::numeric       as rem_seconds,
    (payload->'dailySleepDTO'->>'awakeSleepSeconds')::numeric     as awake_seconds,
    (payload->'dailySleepDTO'->'sleepScores'->'overall'->>'value')::numeric as sleep_score,
    (payload->>'avgOvernightHrv')::numeric                        as avg_overnight_hrv,
    (payload->>'restingHeartRate')::numeric                       as resting_hr,
    ingested_at
from {{ source('raw', 'garmin_sleep') }}
