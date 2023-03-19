import os
import psutil
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time


load_dotenv()

# Set up the InfluxDB 2 client and write API
url = "http://localhost:8086"
token = os.getenv('DOCKER_INFLUXDB_INIT_ADMIN_TOKEN')
org = os.getenv('DOCKER_INFLUXDB_INIT_ORG')
bucket = os.getenv('DOCKER_INFLUXDB_INIT_BUCKET')

# Create a client for InfluxDB 2
client = InfluxDBClient(url=url, token=token)

# Create a new write api for the bucket
write_api = client.write_api(write_options=SYNCHRONOUS)

while True:
    # Get information about all running processes
    processes = psutil.process_iter()

    # Create a list of points to write to InfluxDB
    points = []
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


            # Add the point to the list
            points.append(point)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    # Write the points to InfluxDB
    write_api.write(bucket=bucket, org= org, record=points)
    time.sleep(60)