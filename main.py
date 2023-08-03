"""ookla speedtest exporter"""

import os
import platform
from prometheus_client import start_http_server, Gauge
import time
import json
import subprocess

PRINT_SPACING = "################################"
SOCKET_ERROR = 'Cannot open socket'
DEFAULT_METRIC_VALUE = 0
LINUX = False
if platform.system() == "Linux":
    print("Running on Linux")
    LINUX = True
elif platform.system() == "Windows":
    print("Running on Windows")
def retrieve_results():
    speedtest_output = subprocess.run(
                    ["speedtest", "-f", "json"], capture_output=True)
    return json.loads(speedtest_output.stdout)

class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, polling_interval_seconds=600):
        self.polling_interval_seconds = polling_interval_seconds

        # Prometheus metrics to collect
        self.ping_latency = Gauge("ping_latency_ms", "Current ping latency in milliseconds")
        self.ping_jitter = Gauge("ping_jitter_ms", "Current ping jitter in milliseconds")
        if LINUX:
            self.download_latency = Gauge("download_latency_ms", "Current download latency in milliseconds")
            self.download_jitter = Gauge("download_jitter_ms", "Current download jitter in milliseconds")
        self.download_bandwidth = Gauge("download_bandwidth_bytes", "Current Download bandwidth in bytes")
        if LINUX:
            self.upload_latency = Gauge("upload_latency_ms", "Current upload latency in milliseconds")
            self.upload_jitter = Gauge("upload_jitter_ms", "Current upload jitter in milliseconds")
        self.upload_bandwidth = Gauge("upload_bandwidth_bytes", "Current Upload bandwidth in bytes")
        print("initiated")

    def run_metrics_loop(self):
        """Metrics fetching loop"""
        print("running loop")
        while True:
            self.fetch(0)
            time.sleep(self.polling_interval_seconds)

    def fetch(self,count):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """
        print("fetching data")

        # Fetch raw status data
        json_output = ''
        try:
            json_output = retrieve_results()
            ping_latency_ms = json_output.get("ping", {}).get("latency", 0)
            ping_jitter_ms = json_output.get("ping", {}).get("jitter", 0)
            if LINUX:
                download_latency_ms = json_output.get("download", {}).get("latency", {}).get("iqm", 0)
                download_jitter_ms = json_output.get("download", {}).get("latency", {}).get("jitter", 0)
            download_bandwidth_bytes = json_output.get("download", {}).get("bandwidth", 0) * 8
            if LINUX:
                upload_latency_ms = json_output.get("upload", {}).get("latency", {}).get("iqm", 0)
                upload_jitter_ms = json_output.get("upload", {}).get("latency", {}).get("jitter", 0)
            upload_bandwidth_bytes = json_output.get("upload", {}).get("bandwidth", 0) * 8
            print("fetched data!")
        except Exception as e:
            print("exporter had exception:")
            print(json_output)
            print(PRINT_SPACING)
            print(e.args)
            if json_output.get('error') == SOCKET_ERROR and count < 5:
                count = count + 1
                print("trying again...")
                self.fetch(count)
            
            # default value for if try didnt succeed
            ping_latency_ms = DEFAULT_METRIC_VALUE
            ping_jitter_ms = DEFAULT_METRIC_VALUE
            download_latency_ms = DEFAULT_METRIC_VALUE
            download_jitter_ms = DEFAULT_METRIC_VALUE
            download_bandwidth_bytes = DEFAULT_METRIC_VALUE
            upload_latency_ms = DEFAULT_METRIC_VALUE
            upload_jitter_ms = DEFAULT_METRIC_VALUE
            upload_bandwidth_bytes = DEFAULT_METRIC_VALUE

        # Update Prometheus metrics with fetched metrics
        self.ping_latency.set(ping_latency_ms)
        self.ping_jitter.set(ping_jitter_ms)
        if LINUX:
            self.download_latency.set(download_latency_ms)
            self.download_jitter.set(download_jitter_ms)
        self.download_bandwidth.set(download_bandwidth_bytes)
        if LINUX:
            self.upload_latency.set(upload_latency_ms)
            self.upload_jitter.set(upload_jitter_ms)
        self.upload_bandwidth.set(upload_bandwidth_bytes)

def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "300"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "2313"))

    app_metrics = AppMetrics(
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port)
    print(f"Listening on port {exporter_port}")
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()
