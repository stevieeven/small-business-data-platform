SELECT
    property_id,
    property_name,
    units
FROM {{ source('raw', 'properties') }}