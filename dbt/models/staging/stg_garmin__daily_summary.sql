select
    calendar_date,
    (payload->>'totalSteps')::numeric::int          as total_steps,
    (payload->>'dailyStepGoal')::numeric::int       as step_goal,
    (payload->>'totalDistanceMeters')::numeric      as distance_m,
    (payload->>'totalKilocalories')::numeric        as total_kcal,
    (payload->>'activeKilocalories')::numeric       as active_kcal,
    (payload->>'restingHeartRate')::numeric         as resting_hr,
    (payload->>'minHeartRate')::numeric             as min_hr,
    (payload->>'maxHeartRate')::numeric             as max_hr,
    (payload->>'averageStressLevel')::numeric       as avg_stress,
    (payload->>'bodyBatteryHighestValue')::numeric  as body_battery_high,
    (payload->>'bodyBatteryLowestValue')::numeric   as body_battery_low,
    (payload->>'floorsAscended')::numeric           as floors_ascended,
    (payload->>'moderateIntensityMinutes')::numeric as moderate_intensity_min,
    (payload->>'vigorousIntensityMinutes')::numeric as vigorous_intensity_min,
    ingested_at
from {{ source('raw', 'garmin_daily_summary') }}
