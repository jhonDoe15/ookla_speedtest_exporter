"""ookla speedtest exporter"""

import os
from prometheus_client import start_http_server, Gauge
import time
import json
import subprocess

class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, polling_interval_seconds=600):
        self.polling_interval_seconds = polling_interval_seconds

        # Prometheus metrics to collect
        self.download = Gauge("current_download_speed_bits", "Current Download")
        self.upload = Gauge("current_upload_speed_bits", "Current Upload")
        print("initiated")

    def run_metrics_loop(self):
        """Metrics fetching loop"""
        print("running loop")
        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """
        print("fetching data")

        # Fetch raw status data
        try:
            speedtest_output = subprocess.run(
                    ["speedtest", "-f", "json"], capture_output=True)
            json_output = json.loads(speedtest_output.stdout)
            download_speed_in_bits = json_output['download']['bandwidth'] * 8
            upload_speed_in_bits = json_output['upload']['bandwidth'] * 8
        except Exception as e:
            print("exporter had exception:")
            print(e)
            
            # default value for if try didnt succeed
            download_speed_in_bits = 0
            upload_speed_in_bits = 0

        # Update Prometheus metrics with fetched metrics
        self.download.set(download_speed_in_bits)
        self.upload.set(upload_speed_in_bits)

def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "300"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "2313"))

    app_metrics = AppMetrics(
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port)
    print("Listening on port %s" % exporter_port)
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()
