SELECT
    SUM(total_units) AS total_units,
    SUM(occupied_units) AS occupied_units,
    SUM(vacant_units) AS vacant_units,

    ROUND(
        1.0 * SUM(occupied_units)
        / NULLIF(SUM(total_units), 0),
        3
    ) AS occupancy_rate,

    SUM(potential_rent) AS potential_rent,

    SUM(potential_rent) - SUM(scheduled_rent) AS vacancy_loss,

    SUM(scheduled_rent) AS scheduled_rent,

    SUM(rent_collected) AS rent_collected,

    SUM(outstanding_rent) AS outstanding_rent,

    ROUND(
        1.0 * SUM(rent_collected)
        / NULLIF(SUM(scheduled_rent), 0),
        3
    ) AS collection_rate,

    SUM(total_expenses) AS total_expenses,

    SUM(net_operating_income) AS net_operating_income

FROM {{ ref('property_performance') }}