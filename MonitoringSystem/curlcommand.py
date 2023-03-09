import time
import requests
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# set up the InfluxDB 2 client and write API
url = "http://localhost:8086"
token = "1e0f0fb3581650107a7fd380eae201d7ed681b011497a7a9328ac62afa6e61f5"
org = "monitoring_system"
bucket = "monitoring_database"
client = InfluxDBClient(url=url, token=token)

# Function to retrieve worker data
def get_worker_data():
    response = requests.get("http://localhost:8000/2016-11-01/health/workers")
    workers = response.json()
    return workers

# Write worker data to InfluxDB every 60 seconds
while True:
    workers = get_worker_data()
    write_api = client.write_api(write_options=SYNCHRONOUS)
    for worker in workers:
        point = Point("Lambda_stats") \
            .tag("FuncArn", worker["FuncArn"]) \
            .tag("WorkerId", worker["WorkerId"]) \
            .field("ProcessId", worker["ProcessId"]) \
            .tag("WorkerState", worker["WorkerState"])
        write_api.write(bucket=bucket, org=org, record=point)
    time.sleep(60)
