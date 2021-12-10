# ookla_speedtest_exporter
export metrics about current available network badwidth (download, upload and latency) using ookla speedtest cli

# Usage
install the cli from this link https://www.speedtest.net/apps/cli and add executable to PATH

install dependencies `pip3 install -r requirements.txt`

Linux:
run in background `nohup python3 main.py &`
windows:
`python3 main.py`


exporter base code from https://trstringer.com/quick-and-easy-prometheus-exporter/

