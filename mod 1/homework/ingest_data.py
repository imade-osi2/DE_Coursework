import argparse
import pandas as pd
import requests
from sqlalchemy import create_engine
from pathlib import Path

GREEN_TABLE = "green_tripdata_2025_11"
ZONES_TABLE = "taxi_zone_lookup"

GREEN_URL_DEFAULT = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet"
ZONES_URL_DEFAULT = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

def download_file(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

def ingest_green(engine, parquet_path: Path) -> None:
    # For this homework file, pandas+pyarrow is fine (simple + reliable).
    df = pd.read_parquet(parquet_path)

    # Standardize datetime types (helps with SQL predicates)
    for col in ["lpep_pickup_datetime", "lpep_dropoff_datetime"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])

    # Replace table for repeatable runs
    df.to_sql(GREEN_TABLE, con=engine, if_exists="replace", index=False)
    print(f"Loaded {len(df):,} rows into {GREEN_TABLE}")

def ingest_zones(engine, csv_path: Path) -> None:
    df = pd.read_csv(csv_path)
    df.to_sql(ZONES_TABLE, con=engine, if_exists="replace", index=False)
    print(f"Loaded {len(df):,} rows into {ZONES_TABLE}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default="5433")
    parser.add_argument("--db", default="ny_taxi")
    parser.add_argument("--user", default="postgres")
    parser.add_argument("--password", default="postgres")
    parser.add_argument("--green_url", default=GREEN_URL_DEFAULT)
    parser.add_argument("--zones_url", default=ZONES_URL_DEFAULT)
    args = parser.parse_args()

    engine = create_engine(
        f"postgresql://{args.user}:{args.password}@{args.host}:{args.port}/{args.db}"
    )

    data_dir = Path(__file__).resolve().parent / "data"
    green_path = data_dir / "green_tripdata_2025-11.parquet"
    zones_path = data_dir / "taxi_zone_lookup.csv"

    print("Downloading files...")
    download_file(args.green_url, green_path)
    download_file(args.zones_url, zones_path)

    print("Ingesting into Postgres...")
    ingest_green(engine, green_path)
    ingest_zones(engine, zones_path)

if __name__ == "__main__":
    main()
