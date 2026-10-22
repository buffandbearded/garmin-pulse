with daily as (
    select * from {{ ref('stg_garmin__daily_summary') }}
),
sleep as (
    select * from {{ ref('stg_garmin__sleep') }}
),
workouts as (
    select
        start_time_local::date as calendar_date,
        count(*)               as workout_count,
        sum(duration_s) / 60.0 as workout_minutes
    from {{ ref('stg_garmin__activities') }}
    group by 1
)
select
    d.calendar_date,
    d.total_steps,
    d.step_goal,
    (d.total_steps >= d.step_goal)                  as step_goal_met,
    d.distance_m,
    d.total_kcal,
    d.active_kcal,
    coalesce(d.resting_hr, s.resting_hr)            as resting_hr,
    d.avg_stress,
    d.body_battery_high,
    d.body_battery_low,
    round(s.sleep_seconds / 3600.0, 2)              as sleep_hours,
    round(s.deep_seconds / 3600.0, 2)               as deep_hours,
    round(s.rem_seconds / 3600.0, 2)                as rem_hours,
    s.sleep_score,
    s.avg_overnight_hrv,
    coalesce(w.workout_count, 0)                    as workout_count,
    round(coalesce(w.workout_minutes, 0), 1)        as workout_minutes
from daily d
left join sleep s using (calendar_date)
left join workouts w using (calendar_date)
