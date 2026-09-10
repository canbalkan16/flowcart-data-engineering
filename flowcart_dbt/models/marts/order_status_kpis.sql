select
    status,
    count(*) as total_orders,
    sum(quantity) as total_units
from {{ ref('stg_orders') }}
group by status
order by total_orders desc
