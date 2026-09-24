import random
from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


# Make generated data repeatable
random.seed(42)


properties = [
    {"property_id": "P001", "property_name": "1842 N Kedzie Ave", "units": 12},
    {"property_id": "P002", "property_name": "2715 W Diversey Ave", "units": 16},
    {"property_id": "P003", "property_name": "3056 N Milwaukee Ave", "units": 10},
    {"property_id": "P004", "property_name": "1640 W North Ave", "units": 14},
    {"property_id": "P005", "property_name": "2217 N California Ave", "units": 12},
    {"property_id": "P006", "property_name": "3432 W Fullerton Ave", "units": 18},
    {"property_id": "P007", "property_name": "1925 N Western Ave", "units": 10},
    {"property_id": "P008", "property_name": "2841 W Armitage Ave", "units": 14},
    {"property_id": "P009", "property_name": "3150 N Central Park Ave", "units": 12},
    {"property_id": "P010", "property_name": "2524 W Belmont Ave", "units": 16},
    {"property_id": "P011", "property_name": "1735 N Rockwell St", "units": 10},
    {"property_id": "P012", "property_name": "2908 W Logan Blvd", "units": 14},
    {"property_id": "P013", "property_name": "3317 W Diversey Ave", "units": 12},
    {"property_id": "P014", "property_name": "2136 N Humboldt Blvd", "units": 10},
]


df_properties = pd.DataFrame(properties)

output_file = RAW_DATA_DIR / "properties.csv"
df_properties.to_csv(output_file, index=False)

print(f"Created {output_file}")
print(f"Properties: {len(df_properties)}")
print(f"Total units: {df_properties['units'].sum()}")

# ---------------------------------------------------------
# Generate rent roll
# ---------------------------------------------------------

from datetime import date, timedelta

first_names = [
    "Maria", "James", "David", "Ashley", "Carlos",
    "Jennifer", "Michael", "Nicole", "Daniel", "Sofia",
    "Marcus", "Emily", "Luis", "Rachel", "Anthony"
]

last_names = [
    "Garcia", "Johnson", "Williams", "Martinez", "Brown",
    "Rodriguez", "Davis", "Lopez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Lee"
]

rent_roll = []

report_date = date(2026, 9, 14)

for prop in properties:

    for unit_num in range(1, prop["units"] + 1):

        # Roughly 94% occupancy
        occupied = random.random() < 0.94

        # Generate a realistic monthly rent
        monthly_rent = random.randrange(1400, 2600, 50)

        if occupied:

            tenant_name = (
                f"{random.choice(first_names)} "
                f"{random.choice(last_names)}"
            )

            lease_start = report_date - timedelta(
                days=random.randint(30, 330)
            )

            lease_end = lease_start + timedelta(days=365)

            occupancy_status = "Occupied"

            # Most tenants have paid in full.
            payment_roll = random.random()

            if payment_roll < 0.85:
                amount_paid = monthly_rent

            elif payment_roll < 0.95:
                amount_paid = random.randrange(
                    500,
                    monthly_rent,
                    50
                )

            else:
                amount_paid = 0

            balance_due = monthly_rent - amount_paid

        else:

            tenant_name = None
            lease_start = None
            lease_end = None
            occupancy_status = "Vacant"
            amount_paid = 0
            balance_due = 0

        rent_roll.append({
            "property_id": prop["property_id"],
            "property_name": prop["property_name"],
            "unit_number": unit_num,
            "tenant_name": tenant_name,
            "monthly_rent": monthly_rent,
            "amount_paid": amount_paid,
            "balance_due": balance_due,
            "lease_start": lease_start,
            "lease_end": lease_end,
            "occupancy_status": occupancy_status,
            "report_date": report_date
        })


df_rent_roll = pd.DataFrame(rent_roll)

# Unit numbers can contain source-system formatting variations,
# so treat them as strings rather than integers.
df_rent_roll["unit_number"] = (
    df_rent_roll["unit_number"].astype(str)
)

rent_roll_file = RAW_DATA_DIR / "rent_roll.csv"

# ---------------------------------------------------------
# Simulate real-world source data quality issues
# ---------------------------------------------------------

# Property-name inconsistencies
# Property-name inconsistencies
property_variations = {
    "1842 N Kedzie Ave": "1842 N. Kedzie",
    "2715 W Diversey Ave": "2715 W DIVERSEY",
    "3056 N Milwaukee Ave": "3056 N Milwaukee"
}

for original_name, messy_name in property_variations.items():

    # Find rows belonging specifically to this property
    matching_rows = df_rent_roll[
        df_rent_roll["property_name"] == original_name
        ]

    # Select a few rows from that property
    sample_rows = matching_rows.sample(
        n=min(3, len(matching_rows)),
        random_state=42
    )

    # Introduce the inconsistent name
    df_rent_roll.loc[
        sample_rows.index,
        "property_name"
    ] = messy_name


# Unit-number inconsistencies
unit_sample = df_rent_roll.sample(frac=0.05, random_state=21)

for index in unit_sample.index:
    unit = df_rent_roll.loc[index, "unit_number"]
    df_rent_roll.loc[index, "unit_number"] = f"Unit {unit}"


# Occupancy-status inconsistencies
status_sample = df_rent_roll.sample(frac=0.04, random_state=84)

for index in status_sample.index:
    if df_rent_roll.loc[index, "occupancy_status"] == "Occupied":
        df_rent_roll.loc[index, "occupancy_status"] = "occupied"
    else:
        df_rent_roll.loc[index, "occupancy_status"] = "VACANT"

df_rent_roll.to_csv(
    rent_roll_file,
    index=False
)

print()
print(f"Created {rent_roll_file}")
print(f"Units: {len(df_rent_roll)}")
print(
    f"Occupied: "
    f"{(df_rent_roll['occupancy_status'] == 'Occupied').sum()}"
)
print(
    f"Vacant: "
    f"{(df_rent_roll['occupancy_status'] == 'Vacant').sum()}"
)
print(
    f"Outstanding rent: "
    f"${df_rent_roll['balance_due'].sum():,.2f}"
)

# ---------------------------------------------------------
# Generate QuickBooks-style expenses
# ---------------------------------------------------------

from datetime import datetime

expense_categories = {
    "Utilities": [
        "ComEd",
        "Peoples Gas",
        "City Water"
    ],
    "Cleaning": [
        "Lakeview Cleaning",
        "Windy City Janitorial"
    ],
    "Landscaping": [
        "Green Chicago Landscaping"
    ],
    "Pest Control": [
        "Chicago Pest Solutions"
    ],
    "Repairs": [
        "Northside Handyman",
        "Lakeside Contractors"
    ],
    "Insurance": [
        "Midwest Property Insurance"
    ]
}

expenses = []

transaction_counter = 1

start_date = date(2026, 8, 1)
end_date = date(2026, 9, 14)

for prop in properties:

    # Generate 8-15 ordinary expenses per property
    number_of_expenses = random.randint(8, 15)

    for _ in range(number_of_expenses):

        category = random.choice(
            list(expense_categories.keys())
        )

        vendor = random.choice(
            expense_categories[category]
        )

        days_between = (end_date - start_date).days

        expense_date = start_date + timedelta(
            days=random.randint(0, days_between)
        )

        # Different categories tend to have different costs
        if category == "Utilities":
            amount = random.randrange(200, 900, 25)

        elif category == "Insurance":
            amount = random.randrange(500, 1500, 50)

        elif category == "Repairs":
            amount = random.randrange(150, 1200, 25)

        else:
            amount = random.randrange(100, 700, 25)

        expenses.append({
            "transaction_id": f"TXN{transaction_counter:05d}",
            "property_name": prop["property_name"],
            "expense_date": expense_date,
            "vendor": vendor,
            "category": category,
            "description": f"{category} expense",
            "amount": amount
        })

        transaction_counter += 1

        # ---------------------------------------------------------
# Inject unusually high maintenance spending
# at 3432 W Fullerton Ave
# ---------------------------------------------------------

fullerton_expenses = [
    (
        "2026-08-08",
        "ABC Plumbing",
        "Plumbing",
        "Emergency plumbing repair",
        1850
    ),
    (
        "2026-08-17",
        "ABC Plumbing",
        "Plumbing",
        "Pipe replacement",
        2400
    ),
    (
        "2026-08-29",
        "Chicago Water Restoration",
        "Water Damage",
        "Water damage remediation",
        1750
    ),
    (
        "2026-09-04",
        "ABC Plumbing",
        "Plumbing",
        "Follow-up plumbing repair",
        1300
    ),
    (
        "2026-09-11",
        "Northside Drywall",
        "Repairs",
        "Wall and ceiling repair",
        1900
    )
]

for (
        expense_date,
        vendor,
        category,
        description,
        amount
) in fullerton_expenses:

    expenses.append({
        "transaction_id": f"TXN{transaction_counter:05d}",

        # Intentionally inconsistent with master data!
        "property_name": "3432 W. Fullerton",

        "expense_date": expense_date,
        "vendor": vendor,
        "category": category,
        "description": description,
        "amount": amount
    })

    transaction_counter += 1

df_expenses = pd.DataFrame(expenses)

expenses_file = RAW_DATA_DIR / "expenses.csv"

df_expenses.to_csv(
    expenses_file,
    index=False
)

print()
print(f"Created {expenses_file}")
print(f"Expense transactions: {len(df_expenses)}")
print(
    f"Total expenses: "
    f"${df_expenses['amount'].sum():,.2f}"
)

# ---------------------------------------------------------
# Generate maintenance work orders
# ---------------------------------------------------------

maintenance_categories = [
    "Plumbing",
    "Electrical",
    "HVAC",
    "Appliance",
    "Painting",
    "General Repair",
    "Pest Control"
]

maintenance_vendors = [
    "Northside Handyman",
    "ABC Plumbing",
    "Chicago Electric",
    "Windy City HVAC",
    "Lakeside Contractors"
]

work_orders = []
work_order_counter = 1

for prop in properties:

    number_of_orders = random.randint(4, 10)

    for _ in range(number_of_orders):

        reported_date = start_date + timedelta(
            days=random.randint(
                0,
                (end_date - start_date).days
            )
        )

        completed = random.random() < 0.80

        if completed:
            completed_date = reported_date + timedelta(
                days=random.randint(1, 10)
            )
            status = "Completed"
        else:
            completed_date = None
            status = "Open"

        category = random.choice(maintenance_categories)
        vendor = random.choice(maintenance_vendors)

        unit_number = str(
            random.randint(1, prop["units"])
        )

        cost = random.randrange(100, 1200, 25)

        work_orders.append({
            "work_order_id": f"WO{work_order_counter:05d}",
            "property_name": prop["property_name"],
            "unit_number": unit_number,
            "reported_date": reported_date,
            "completed_date": completed_date,
            "category": category,
            "status": status,
            "vendor": vendor,
            "cost": cost,
            "notes": f"{category} service request"
        })

        work_order_counter += 1


df_maintenance = pd.DataFrame(work_orders)

# ---------------------------------------------------------
# Simulate maintenance data-quality issues
# ---------------------------------------------------------

# Inconsistent property names
maintenance_property_variations = {
    "1842 N Kedzie Ave": "1842 Kedzie",
    "3432 W Fullerton Ave": "3432 W. Fullerton",
    "2908 W Logan Blvd": "2908 Logan Boulevard"
}

for original_name, messy_name in (
        maintenance_property_variations.items()
):

    matching_rows = df_maintenance[
        df_maintenance["property_name"] == original_name
        ]

    if not matching_rows.empty:

        sample_rows = matching_rows.sample(
            n=min(2, len(matching_rows)),
            random_state=42
        )

        df_maintenance.loc[
            sample_rows.index,
            "property_name"
        ] = messy_name


# Inconsistent status values
status_sample = df_maintenance.sample(
    frac=0.05,
    random_state=42
)

for index in status_sample.index:

    if df_maintenance.loc[index, "status"] == "Completed":
        df_maintenance.loc[index, "status"] = "COMPLETE"
    else:
        df_maintenance.loc[index, "status"] = "open"


# ---------------------------------------------------------
# Create duplicate work orders
# ---------------------------------------------------------

duplicate_rows = df_maintenance.sample(
    n=5,
    random_state=42
).copy()

df_maintenance = pd.concat(
    [df_maintenance, duplicate_rows],
    ignore_index=True
)

maintenance_file = RAW_DATA_DIR / "maintenance.csv"

df_maintenance.to_csv(
    maintenance_file,
    index=False
)

print()
print(f"Created {maintenance_file}")
print(
    f"Maintenance rows including duplicates: "
    f"{len(df_maintenance)}"
)
print(
    f"Unique work orders: "
    f"{df_maintenance['work_order_id'].nunique()}"
)
print(
    f"Duplicate rows: "
    f"{len(df_maintenance) - df_maintenance['work_order_id'].nunique()}"
)