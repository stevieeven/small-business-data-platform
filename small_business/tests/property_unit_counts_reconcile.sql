SELECT
    property_id,
    property_name,
    total_units,
    occupied_units,
    vacant_units

FROM {{ ref('property_performance') }}

WHERE occupied_units + vacant_units <> total_units