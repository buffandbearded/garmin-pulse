-- Fails if any sleep score is outside 0-100
select calendar_date, sleep_score
from {{ ref('fct_daily_health') }}
where sleep_score is not null and sleep_score not between 0 and 100
