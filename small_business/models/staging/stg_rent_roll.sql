WITH rent_roll AS (

    SELECT
        property_id,
        property_name,
        REPLACE(unit_number, 'Unit ', '') AS unit_number,
        tenant_name,
        monthly_rent,
        amount_paid,
        balance_due,
        CAST(lease_start AS DATE) AS lease_start,
        CAST(lease_end AS DATE) AS lease_end,

        CASE
            WHEN LOWER(occupancy_status) = 'occupied' THEN 'Occupied'
            WHEN LOWER(occupancy_status) = 'vacant' THEN 'Vacant'
            ELSE occupancy_status
        END AS occupancy_status,

        CAST(report_date AS DATE) AS report_date

    FROM {{ source('raw', 'rent_roll') }}

),

properties AS (

    SELECT
        property_id,
        property_name
    FROM {{ ref('stg_properties') }}

)

SELECT
    rent_roll.property_id,

    properties.property_name,

    rent_roll.unit_number,
    rent_roll.tenant_name,
    rent_roll.monthly_rent,
    rent_roll.amount_paid,
    rent_roll.balance_due,
    rent_roll.lease_start,
    rent_roll.lease_end,
    rent_roll.occupancy_status,
    rent_roll.report_date

FROM rent_roll

LEFT JOIN properties
    ON rent_roll.property_id = properties.property_id