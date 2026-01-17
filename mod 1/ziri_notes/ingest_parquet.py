import argparse
import pandas as pd
from sqlalchemy import create_engine
import requests
import io

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    # Download the parquet file with SSL verification disabled (for macOS SSL issues)
    response = requests.get(url, verify=False)
    response.raise_for_status()
    df = pd.read_parquet(io.BytesIO(response.content))

    # Clean column names for Postgres
    df.columns = [c.strip().lower() for c in df.columns]

    engine = create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{db}"
    )

    # Create table and insert data in chunks
    df.head(0).to_sql(name=table_name, con=engine, if_exists='replace', index=False)

    chunk_size = 100000
    for i in range(0, len(df), chunk_size):
        df.iloc[i:i+chunk_size].to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False
        )
        print(f"Inserted rows {i} to {min(i+chunk_size, len(df))}")

    print("Ingestion completed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest Parquet data to Postgres')
    parser.add_argument('--user', required=True, help='Postgres user')
    parser.add_argument('--password', required=True, help='Postgres password')
    parser.add_argument('--host', required=True, help='Postgres host')
    parser.add_argument('--port', required=True, help='Postgres port')
    parser.add_argument('--db', required=True, help='Postgres database')
    parser.add_argument('--table_name', required=True, help='Target table name')
    parser.add_argument('--url', required=True, help='URL of the Parquet file')

    args = parser.parse_args()
    main(args)