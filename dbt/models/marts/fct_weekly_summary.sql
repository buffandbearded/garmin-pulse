select
    date_trunc('week', calendar_date)::date        as week_start,
    count(*)                                       as days_tracked,
    round(avg(total_steps))                        as avg_steps,
    round(avg(sleep_hours), 2)                     as avg_sleep_hours,
    round(avg(sleep_score), 1)                     as avg_sleep_score,
    round(avg(resting_hr), 1)                      as avg_resting_hr,
    round(avg(avg_overnight_hrv), 1)               as avg_hrv,
    round(avg(avg_stress), 1)                      as avg_stress,
    sum(workout_count)                             as workouts,
    sum(workout_minutes)                           as workout_minutes,
    sum(step_goal_met::int)                        as days_step_goal_met
from {{ ref('fct_daily_health') }}
group by 1
