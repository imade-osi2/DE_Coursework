import argparse
import pandas as pd
from sqlalchemy import create_engine
import requests  # Add this import
import io  # Add this import

def main(args):
    # Download the Parquet file with SSL verification disabled
    response = requests.get(args.url, verify=False)
    response.raise_for_status()  # Raise an error if the download fails
    
    # Read Parquet directly from the downloaded bytes
    df = pd.read_parquet(io.BytesIO(response.content))

    # ...existing code...
    # Basic cleanup: ensure column names are postgres-friendly
    df.columns = [c.strip().lower() for c in df.columns]

    engine = create_engine(
        f"postgresql://{args.user}:{args.password}@{args.host}:{args.port}/{args.db}"
    )

    # Load: create/replace table then append in chunks for stability
    df.head(0).to_sql(name=args.table_name, con=engine, if_exists="replace", index=False)

    chunk_size = args.chunk_size
    for i in range(0, len(df), chunk_size):
        df.iloc[i:i+chunk_size].to_sql(
            name=args.table_name,
            con=engine,
            if_exists="append",
            index=False
        )
        print(f"Loaded rows {i} to {min(i+chunk_size, len(df))}")

    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="root")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--db", default="ny_taxi")
    parser.add_argument("--table_name", default="yellow_tripdata_2025_01")
    parser.add_argument("--url", required=True)
    parser.add_argument("--chunk_size", type=int, default=100000)
    args = parser.parse_args()
    main(args)