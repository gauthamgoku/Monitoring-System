import os
import time
import requests
import psutil
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()

# Set up the InfluxDB 2 client and write API
url = "http://localhost:8086"
token = os.getenv('DOCKER_INFLUXDB_INIT_ADMIN_TOKEN')
org = os.getenv('DOCKER_INFLUXDB_INIT_ORG')
bucket = os.getenv('DOCKER_INFLUXDB_INIT_BUCKET')
client = InfluxDBClient(url=url, token=token)

# Function to retrieve worker data
def get_worker_data():
    response = requests.get("http://localhost:8000/2016-11-01/health/workers")
    workers = response.json()
    return workers

# Write process and worker data to InfluxDB every 60 seconds
while True:
    # Get information about all running processes
    processes = psutil.process_iter()

    # Retrieve worker data from the AWS Lambda Health API
    workers = get_worker_data()

    # Create a write API object for the bucket
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Write process data to InfluxDB
    for proc in processes:
        try:
            # Get process information
            info = proc.as_dict(attrs=["pid", "name", "cpu_percent", "memory_percent", "status"])

            # Create a point for the process
            point = Point("processes")
            point.tag("process_name", info["name"])
            point.tag("process_status", info["status"])
            point.field("process_pid", info["pid"])
            point.field("process_cpu_percent", info["cpu_percent"])
            point.field("process_memory_percent", info["memory_percent"])

            # Add the point to the write API
            write_api.write(bucket=bucket, org=org, record=point)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Write worker data to InfluxDB
    for worker in workers:
        point = Point("Lambda_stats") \
            .tag("FuncArn", worker["FuncArn"]) \
            .field("WorkerId", worker["WorkerId"]) \
            .field("ProcessId", worker["ProcessId"]) \
            .field("WorkerState", worker["WorkerState"])
        write_api.write(bucket=bucket, org=org, record=point)

    # Sleep for 60 seconds before repeating the process
    time.sleep(60)
