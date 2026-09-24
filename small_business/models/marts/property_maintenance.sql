WITH maintenance AS (

    SELECT
        property_id,
        category,
        status,
        cost

    FROM {{ ref('stg_maintenance') }}
),

properties AS (

    SELECT
        property_id,
        property_name

    FROM {{ ref('stg_properties') }}
)

SELECT
    maintenance.property_id,
    properties.property_name,
    maintenance.category,

    COUNT(*) AS work_order_count,

    SUM(
        CASE
            WHEN maintenance.status = 'Open' THEN 1
            ELSE 0
        END
    ) AS open_work_orders,

    SUM(
        CASE
            WHEN maintenance.status = 'Completed' THEN 1
            ELSE 0
        END
    ) AS completed_work_orders,

    SUM(maintenance.cost) AS maintenance_cost

FROM maintenance

LEFT JOIN properties
    ON maintenance.property_id = properties.property_id

GROUP BY
    maintenance.property_id,
    properties.property_name,
    maintenance.category