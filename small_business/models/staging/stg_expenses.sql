WITH expenses AS (

    SELECT
        transaction_id,
        property_name,
        CAST(expense_date AS DATE) AS expense_date,
        vendor,
        category,
        description,
        amount

    FROM {{ source('raw', 'expenses') }}

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
    expenses.transaction_id,

    COALESCE(
        properties.property_id,
        property_mapping.property_id
    ) AS property_id,

    expenses.property_name,
    expenses.expense_date,
    expenses.vendor,
    expenses.category,
    expenses.description,
    expenses.amount

FROM expenses

LEFT JOIN properties
    ON expenses.property_name = properties.property_name

LEFT JOIN property_mapping
    ON expenses.property_name = property_mapping.source_property_name