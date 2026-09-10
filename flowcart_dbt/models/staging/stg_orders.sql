select
    order_id,
    customer_id,
    product_id,
    quantity,
    order_date,
    status,
    last_modified
from {{ source('flowcart', 'orders') }}
