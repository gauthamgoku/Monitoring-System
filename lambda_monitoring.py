import os
import time
import requests
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


load_dotenv()

# Set up the InfluxDB 2 client and write API
url = "http://localhost:8086"
token = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")
org = os.getenv("DOCKER_INFLUXDB_INIT_ORG")
bucket = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET")
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
            .field("WorkerId", worker["WorkerId"]) \
            .field("ProcessId", worker["ProcessId"]) \
            .field("WorkerState", worker["WorkerState"])
        write_api.write(bucket=bucket, org=org, record=point)
    time.sleep(60)
