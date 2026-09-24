WITH rent_performance AS (

    SELECT
        property_id,
        property_name,

        COUNT(*) AS total_units,

        SUM(
            CASE
                WHEN occupancy_status = 'Occupied' THEN 1
                ELSE 0
            END
        ) AS occupied_units,

        SUM(
            CASE
                WHEN occupancy_status = 'Vacant' THEN 1
                ELSE 0
            END
        ) AS vacant_units,

        ROUND(
            100.0 *
            SUM(
                CASE
                    WHEN occupancy_status = 'Occupied' THEN 1
                    ELSE 0
                END
            ) / COUNT(*),
            1
        ) AS occupancy_rate,

        SUM(monthly_rent) AS potential_rent,
        SUM(
            CASE
                WHEN occupancy_status = 'Occupied'
                THEN monthly_rent
                ELSE 0
            END
        ) AS scheduled_rent,
        SUM(amount_paid) AS rent_collected,
        SUM(balance_due) AS outstanding_rent

    FROM {{ ref('stg_rent_roll') }}

    GROUP BY
        property_id,
        property_name

),

expense_totals AS (

    SELECT
        property_id,
        SUM(total_expenses) AS total_expenses

    FROM {{ ref('property_expenses') }}

    GROUP BY property_id

)

SELECT
    rent_performance.property_id,
    rent_performance.property_name,
    rent_performance.total_units,
    rent_performance.occupied_units,
    rent_performance.vacant_units,
    rent_performance.occupancy_rate,
    rent_performance.potential_rent,
    rent_performance.scheduled_rent,
    rent_performance.rent_collected,
    rent_performance.outstanding_rent,
    ROUND(
        100.0 * rent_performance.rent_collected
        / NULLIF(rent_performance.scheduled_rent, 0),
        1
    ) AS collection_rate,
    expense_totals.total_expenses,
    rent_performance.rent_collected
        - COALESCE(expense_totals.total_expenses, 0) AS net_operating_income

FROM rent_performance

LEFT JOIN expense_totals
    ON rent_performance.property_id = expense_totals.property_id