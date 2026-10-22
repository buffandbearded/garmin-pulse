-- Fails if resting heart rate is physiologically implausible
select calendar_date, resting_hr
from {{ ref('fct_daily_health') }}
where resting_hr is not null and resting_hr not between 30 and 120
