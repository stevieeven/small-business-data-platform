SELECT
    property_id,
    property_name,
    scheduled_rent,
    rent_collected,
    outstanding_rent

FROM {{ ref('property_performance') }}

WHERE scheduled_rent <> rent_collected + outstanding_rent