# Environment & Database Setup Guide

Follow these steps to set up your local environment and database for the NYC Taxi Data project.

---

## 1. Create a Project Folder

```sh
mkdir ny_taxi_local_ingest
cd ny_taxi_local_ingest
mkdir data
```

## 2. Start Postgres in Docker (container + volume)

Run this in Terminal from the project folder:

```sh
docker run -d \
  --name ny_taxi_postgres \
  -e POSTGRES_USER=root \
  -e POSTGRES_PASSWORD=root \
  -e POSTGRES_DB=ny_taxi \
  -v "$(pwd)/data:/var/lib/postgresql/data" \
  -p 5432:5432 \
  postgres:16
```

Confirm it’s running:

```sh
docker ps
```

## 3. Connect using pgAdmin Desktop (NOT the container UI)

Open pgAdmin (desktop app) → Add New Server:

**General**

- Name: ny_taxi_local

**Connection**

- Host name/address: localhost
- Port: 5432
- Maintenance database: ny_taxi
- Username: root
- Password: root

Save.

## 4. Set up a local Python environment for VS Code

From the project folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pandas pyarrow sqlalchemy psycopg2-binary
```

## 5. Create the ingestion script in VS Code

Create a file: `ingest_parquet.py`

```python
import argparse
import pandas as pd
from sqlalchemy import create_engine

def main(args):
    # Download + read parquet directly
    df = pd.read_parquet(args.url)

rest of ingestion code............
```

## 6. Run the ingestion script

Make sure your venv is active:

```sh
source .venv/bin/activate
```

Install requests if needed:

```sh
pip install requests
```

Run:

```sh
python ingest_parquet.py \
  --url "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet"
```

## 7. Verify in pgAdmin Desktop

In pgAdmin:

```
Servers → ny_taxi_local → Databases → ny_taxi → Schemas → public → Tables
```

You should see: `yellow_tripdata_2025_01`

Run:

```sql
SELECT COUNT(3) FROM yellow_tripdata_2025_01;
```

or 

```sql
SELECT * FROM yellow_tripdata_2025_01 limit 3;
```