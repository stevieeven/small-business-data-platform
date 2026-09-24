WITH maintenance AS (

    SELECT
        work_order_id,
        property_id,
        unit_number,
        reported_date,
        completed_date,
        category,
        status,
        vendor,
        cost,
        notes

    FROM {{ ref('stg_maintenance') }}
),

properties AS (

    SELECT
        property_id,
        property_name

    FROM {{ ref('stg_properties') }}
)

SELECT
    maintenance.work_order_id,
    maintenance.property_id,
    properties.property_name,
    maintenance.unit_number,
    maintenance.reported_date,
    DATE '2026-09-14' - maintenance.reported_date AS days_open,
    CASE
        WHEN DATE '2026-09-14' - maintenance.reported_date <= 7
            THEN '0-7 days'
        WHEN DATE '2026-09-14' - maintenance.reported_date <= 14
            THEN '8-14 days'
        WHEN DATE '2026-09-14' - maintenance.reported_date <= 30
            THEN '15-30 days'
        ELSE '31+ days'
    END AS age_bucket,
    CASE
        WHEN DATE '2026-09-14' - maintenance.reported_date <= 7 THEN 1
        WHEN DATE '2026-09-14' - maintenance.reported_date <= 14 THEN 2
        WHEN DATE '2026-09-14' - maintenance.reported_date <= 30 THEN 3
        ELSE 4
    END AS age_bucket_sort,
    maintenance.completed_date,
    maintenance.category,
    maintenance.status,
    maintenance.vendor,
    maintenance.cost,
    maintenance.notes

FROM maintenance

LEFT JOIN properties
    ON maintenance.property_id = properties.property_id