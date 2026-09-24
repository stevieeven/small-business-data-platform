WITH expenses AS (

    SELECT
        property_id,
        category,
        COUNT(*) AS transaction_count,
        SUM(amount) AS total_expenses

    FROM {{ ref('stg_expenses') }}

    GROUP BY
        property_id,
        category
),

properties AS (

    SELECT
        property_id,
        property_name

    FROM {{ ref('stg_properties') }}
)

SELECT
    expenses.property_id,
    properties.property_name,
    expenses.category,
    expenses.transaction_count,
    expenses.total_expenses

FROM expenses

LEFT JOIN properties
    ON expenses.property_id = properties.property_id