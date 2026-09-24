from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL
import pandas as pd
from sqlalchemy import create_engine, text


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# ---------------------------------------------------------
# PostgreSQL connection
# ---------------------------------------------------------

# Load local environment configuration
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.environ["POSTGRES_DB"]
)

engine = create_engine(DATABASE_URL)


# ---------------------------------------------------------
# Reusable raw-data loader
# ---------------------------------------------------------

def load_csv_to_postgres(file_name, table_name):
    file_path = RAW_DATA_DIR / file_name

    print()
    print(f"Reading {file_name}...")

    df = pd.read_csv(file_path)

    print(f"Rows read: {len(df)}")

    with engine.begin() as connection:

        connection.execute(
            text(f'TRUNCATE TABLE raw."{table_name}"')
        )

        df.to_sql(
            name=table_name,
            con=connection,
            schema="raw",
            if_exists="append",
            index=False
        )

    print(
        f"Loaded {len(df)} rows "
        f"into raw.{table_name}"
    )


# ---------------------------------------------------------
# Load raw source files
# ---------------------------------------------------------

load_csv_to_postgres(
    "properties.csv",
    "properties"
)

load_csv_to_postgres(
    "rent_roll.csv",
    "rent_roll"
)

load_csv_to_postgres(
    "expenses.csv",
    "expenses"
)

load_csv_to_postgres(
    "maintenance.csv",
    "maintenance"
)

