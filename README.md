# docker-speedtest-influxdbv2

Runs Ookla's [Speedtest CLI](https://www.speedtest.net/apps/cli) program in Docker, sends the results to InfluxDB
  - Source code: [GitHub](https://github.com/coolmule0/docker-speedtest-influxdbv2)
  - Docker container: [Docker Hub](https://hub.docker.com/r/coolmule0/docker-speedtest-influxdbv2)
  - Image base: [Python (slim Buster)](https://hub.docker.com/_/python)
  - Init system: N/A
  - Application: [Speedtest CLI](https://www.speedtest.net/apps/cli)

## Explanation

  - This runs Ooka's Speedtest CLI program on an interval, then writes the data to an InfluxDB database (you can later graph this data with Grafana or Chronograf)
  - This does **NOT** use the open-source [speedtest-cli](https://github.com/sivel/speedtest-cli). That program uses the Speedtest.net HTTP API. This program uses Ookla's official CLI application.
  - ⚠️ Ookla's speedtest application is closed-source (the binary applications are [here](https://bintray.com/ookla)) and Ookla's reasoning for this decision is [here](https://www.reddit.com/r/HomeNetworking/comments/dpalqu/speedtestnet_just_launched_an_official_c_cli/f5tm9up/) ⚠️
  - ⚠️ Ookla's speedtest application reports all data back to Ookla ⚠️

## Requirements

  - This work with InfluxDB 2.0.
  - You must already have an InfluxDB database created, along with a bucket and token that has `WRITE` permissions on that bucket.
  - This Docker container needs to be able to reach that InfluxDB instance by hostname, IP address, or Docker service name (I run this container on the same Docker network as my InfluxDB instance).
  - ⚠️ Depending on how often you run this, you may need to monitor your internet connection's usage. If you have a data cap, you could exceed it. The standard speedtest uses about 750MB of data per run. See below for an example. ⚠️

```
CONTAINER: NET I/O
speedtest: 225MB / 495MB
```

## Docker image information

### Docker image tags
  - `latest`: Latest version
  - `X.X.X`: [Semantic version](https://semver.org/) (use if you want to stick on a specific version)

### Environment variables

| Variable       | Required?                  | Definition                                     | Example                                     | Comments                                                                                         |
|----------------|----------------------------|------------------------------------------------|---------------------------------------------|--------------------------------------------------------------------------------------------------|
| INFLUXDB_V2_URL  | Yes                      | Server URL hosting the InfluxDB with port if necessary   | `http://192.168.1.12:8086` or `http://influxdb:8086`    |                                                                                                  |
| INFLUXDB_V2_ORG  | Yes         | InfluxDB organisation                                  | `my_org`     | Need a pre-created Organisation within Influxdb                                     |
| INFLUXDB_V2_TOKEN  | Yes                        | Access Token                              | `A86b8d9c0c*^jsld==`                             | Needs to have WRITE permissions already                                                 |
| BUCKET    | Yes                        | Bucket name                                  | `speedtest`                              | Must already be created, this does not create a bucket                                               |                                                          |
| SLEEPY_TIME    | No (default: 3600)         | Seconds to sleep between runs                  | `3600`                                        | The loop takes about 15-30 seconds to run, so I wouldn't set this value any lower than 60 (1min) |                                                          |
| SPEEDTEST_HOST | No (default: container ID) | Hostname of service where Speedtest is running | `server04`                                   | Useful if you're running Speedtest on multiple servers                                           |

### Ports
N/A

### Volumes
N/A

### Example usage
Below is an example docker-compose.yml file.
```
version: '3'
services:
  speedtest:
    container_name: tig_speedtest
    restart: unless-stopped
    environment:
      - INFLUXDB_V2_URL=http://influxdb:8086
      - SLEEPY_TIME=7200 #in seconds
      - SPEEDTEST_HOST=my_server
      - INFLUXDB_V2_TOKEN=my_token
      - INFLUXDB_V2_ORG=my_org
      - BUCKET=speedtest
    networks:
      - influx
    image: coolmule0/docker-speedtest-influxdbv2:latest

networks:
  influx:
```

## Changes to upstream version
- Use more modern Influxdb 2 api calls (tokens & orgs, instead of user & password)
- Use the Speedtest Python API