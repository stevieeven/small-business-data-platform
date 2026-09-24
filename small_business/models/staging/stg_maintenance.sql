WITH maintenance AS (

    SELECT
        work_order_id,
        property_name,
        unit_number,
        CAST(reported_date AS DATE) AS reported_date,
        CAST(completed_date AS DATE) AS completed_date,
        category,

        CASE
            WHEN LOWER(status) = 'completed' THEN 'Completed'
            WHEN LOWER(status) = 'complete' THEN 'Completed'
            WHEN LOWER(status) = 'open' THEN 'Open'
            ELSE status
        END AS status,

        vendor,
        cost,
        notes,

        ROW_NUMBER() OVER (
            PARTITION BY work_order_id
            ORDER BY reported_date DESC
        ) AS row_num

    FROM {{ source('raw', 'maintenance') }}

),

properties AS (

    SELECT
        property_id,
        property_name
    FROM {{ ref('stg_properties') }}

),

property_mapping AS (

    SELECT
        source_property_name,
        property_id
    FROM {{ ref('property_name_mapping') }}

)

SELECT
    maintenance.work_order_id,

    COALESCE(
        properties.property_id,
        property_mapping.property_id
    ) AS property_id,

    maintenance.property_name,
    maintenance.unit_number,
    maintenance.reported_date,
    maintenance.completed_date,
    maintenance.category,
    maintenance.status,
    maintenance.vendor,
    maintenance.cost,
    maintenance.notes

FROM maintenance

LEFT JOIN properties
    ON maintenance.property_name = properties.property_name

LEFT JOIN property_mapping
    ON maintenance.property_name = property_mapping.source_property_name

WHERE maintenance.row_num = 1