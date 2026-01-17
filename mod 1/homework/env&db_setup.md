# Environment & Database Setup Guide

Follow these steps to set up your local environment and database for the NYC Taxi Data homework.

---

## 1. Create a Project Folder

**Recommended repo structure:**

```
de-zoomcamp-hw1/
  docker-compose.yaml
  ingest_data.py
```

---

## 2. Docker Compose (Postgres Only)

**Sample `docker-compose.yaml`:**

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

volumes:
  vol-pgdata:
    name: vol-pgdata
```

**Start Postgres:**

```bash
docker compose up -d
```

---

## 3. pgAdmin Desktop App Connection Info

Use the pgAdmin app installed on your laptop to connect:

- **Host:** `localhost`
- **Port:** `5433`
- **Maintenance DB:** `ny_taxi`
- **Username:** `postgres`
- **Password:** `postgres`

> **Note:**  
> - The **pgAdmin container** would use `db:5432` (inside Docker network).  
> - The **pgAdmin desktop app** uses `localhost:5433` (your host-mapped port).

---

## 4. Python Ingestion Script (VS Code, No Jupyter)

From your repo root, set up your environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas pyarrow sqlalchemy psycopg2-binary requests
```

**This loads:**
- Parquet → `green_tripdata_2025_11`
- Zones CSV → `taxi_zone_lookup`

**Example ingestion script (`ingest_data.py`):**

```python
import argparse
import pandas as pd
import requests
from sqlalchemy import create_engine
from pathlib import Path

GREEN_TABLE = "green_tripdata_2025_11"
ZONES_TABLE = "taxi_zone_lookup"

# ...rest of ingestion code...
```

**Run ingestion:**

```bash
source .venv/bin/activate
python ingest_data.py
```

---

## 5. Verify in pgAdmin Desktop

Open pgAdmin desktop and refresh tables. You should see:

- `green_tripdata_2025_11`
- `taxi_zone_lookup`

---

# Homework Questions & SQL

## Q1: pip version in python:3.13

**Run:**

```bash
docker run -it --rm --entrypoint bash python:3.13
```

Inside the container:

```bash
pip --version
```

Match the output to the multiple-choice option.

---

## Q2: Hostname & Port for pgAdmin → Postgres (docker-compose)

- **Hostname:** `db` (service name in docker-compose)
- **Port:** `5432` (container port)

> Your `5433:5432` mapping is only for connecting from your laptop (host).

---

## SQL for Q3–Q6

All queries assume:

- Trips table: `green_tripdata_2025_11`
- Zones table: `taxi_zone_lookup`

---

### Q3: Short trips (≤ 1 mile) in Nov 2025

```sql
SELECT COUNT(*) AS short_trips
FROM green_tripdata_2025_11
WHERE lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime <  '2025-12-01'
  AND trip_distance <= 1;
```

---

### Q4: Pickup day with the longest trip distance (trip_distance < 100)

```sql
SELECT DATE(lpep_pickup_datetime) AS pickup_day
FROM green_tripdata_2025_11
WHERE lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime <  '2025-12-01'
  AND trip_distance < 100
ORDER BY trip_distance DESC
LIMIT 1;
```

---

### Q5: Pickup zone with largest total_amount on Nov 18, 2025

```sql
SELECT z."Zone" AS pickup_zone,
       SUM(t.total_amount) AS total_amount_sum
FROM green_tripdata_2025_11 t
JOIN taxi_zone_lookup z
  ON t."PULocationID" = z."LocationID"
WHERE t.lpep_pickup_datetime >= '2025-11-18'
  AND t.lpep_pickup_datetime <  '2025-11-19'
GROUP BY z."Zone"
ORDER BY total_amount_sum DESC
LIMIT 1;
```

---

### Q6: From pickups in “East Harlem North”, dropoff zone with largest tip

```sql
SELECT zdo."Zone" AS dropoff_zone,
       MAX(t.tip_amount) AS max_tip
FROM green_tripdata_2025_11 t
JOIN taxi_zone_lookup zpu
  ON t."PULocationID" = zpu."LocationID"
JOIN taxi_zone_lookup zdo
  ON t."DOLocationID" = zdo."LocationID"
WHERE t.lpep_pickup_datetime >= '2025-11-01'
  AND t.lpep_pickup_datetime <  '2025-12-01'
  AND zpu."Zone" = 'East Harlem North'
GROUP BY zdo."Zone"
ORDER BY max_tip DESC
LIMIT 1;
```