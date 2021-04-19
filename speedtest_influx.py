#!/usr/bin/env python3

import datetime
import os
import time
import socket
import sys

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import speedtest

# Variables
sleepy_time = int(os.getenv("SLEEPY_TIME", 3600))
start_time = datetime.datetime.utcnow().isoformat()
default_hostname = socket.gethostname()
hostname = os.getenv("SPEEDTEST_HOST", default_hostname)
org = os.getenv("INFLUXDB_V2_ORG")
bucket = os.getenv("BUCKET")
servers = []
threads = None

def db_check():
    print("STATE: Running database check")
    client_health = client.health().status

    if client_health == "pass":
        print("STATE: Connection", client_health)
    elif client_health == "fail":
        print("ERROR: Connection", client_health, " - Check token, org")
        sys.exit(1)
    else:
        print("ERROR: Something else went wrong")
        sys.exit(1)


def speedtest_run():
    db_check()

    current_time = datetime.datetime.utcnow().isoformat()
    print("STATE: Loop running at", current_time)

    # Run Speedtest
    print("STATE: Speedtest running")
    s = speedtest.Speedtest()
    s.get_servers(servers)
    s.get_best_server()
    s.download(threads=threads)
    s.upload(threads=threads)
    s.results.share()

    results_dict = s.results.dict() 

    # Print results to Docker logs
    print("NOTE:  RESULTS ARE SAVED IN BPS NOT MBPS")
    print("STATE: Your download     ", results_dict["download"], "bps")
    print("STATE: Your upload       ", results_dict["upload"], "bps")
    print("STATE: Your ping latency ", results_dict["ping"], "ms")
    print("STATE: Your server info  ", results_dict["server"]["id"], results_dict["server"]["host"], results_dict["server"]["lat"],results_dict["server"]["lon"], results_dict["server"]["country"], results_dict["server"]["host"])
    print("STATE: Your URL is       ", results_dict["share"], " <--- This is not saved to InfluxDB")

    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    # convert speedtest dict to point-ready dict
    point_dict = { "measurement": "speedtest"}
    point_dict["tags"] = {"host": hostname,
                            "server_id": results_dict["server"]["id"],
                            "client_ip": results_dict["client"]["ip"]}
    point_dict["fields"] = {key: results_dict[key] for key in results_dict.keys()
                            & {'download', 'upload', 'ping', 'bytes_sent', 'bytes_received'}}
    point_dict["time"] = results_dict["timestamp"]
    p =  Point.from_dict(point_dict)

    write_api.write(bucket, org, p)

    print("STATE: Sleeping for", sleepy_time, "seconds")
    time.sleep(sleepy_time)


if __name__ == "__main__":
    # Some logging
    print("#####\nScript starting!\n#####")
    print("STATE: Starting at", start_time)
    print("STATE: Sleep time between runs set to", sleepy_time, "seconds")

    # Check if variables are set
    print("STATE: Checking environment variables...")
    if not 'BUCKET' in os.environ:
        print("ERROR: BUCKET is not set")
        sys.exit(1)

    if not 'INFLUXDB_V2_TOKEN' in os.environ:
        print("ERROR: INFLUXDB_V2_TOKEN is not set")
        sys.exit(1)

    if not 'INFLUXDB_V2_ORG' in os.environ:
        print("ERROR: INFLUXDB_V2_ORG is not set")
        sys.exit(1)

    # Instantiate the connection
    print("STATE: Connecting to InfluxDB...")
    client = InfluxDBClient.from_env_properties()

    while True:
        speedtest_run()
