import psutil
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time

# Choose a bucket to store the data in
bucket = "monitoring_database"
org = "monitoring_system"
url = "http://localhost:8086"
token="1e0f0fb3581650107a7fd380eae201d7ed681b011497a7a9328ac62afa6e61f5"

# Create a client for InfluxDB 2
client = InfluxDBClient(url=url, token=token, org=org)

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
            point.tag("process_pid", info["pid"])
            point.field("process_cpu_percent", info["cpu_percent"])
            point.field("process_memory_percent", info["memory_percent"])


            # Add the point to the list
            points.append(point)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    # Write the points to InfluxDB
    write_api.write(bucket=bucket, org= org, record=points)
    time.sleep(60)
