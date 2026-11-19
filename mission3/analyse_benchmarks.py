import pandas as pd
from pathlib import Path

files = {
    "Remote Keep-Alive": "mission3/benchmarks/remote_keepalive.csv",
    "Remote No-Keep-Alive": "mission3/benchmarks/remote_no_keepalive.csv",
    "Localhost": "mission3/benchmarks/localhost.csv"
}

metrics = [
    "round_trip", "parse", "normalise",
    "inference", "build", "server_total",
    "network_and_framework"
]

for name, filename in files.items():
    df = pd.read_csv(filename)

    print(f"\n{'='*65}")
    print(name)
    print(f"{'='*65}")

    print("\nFirst request:")
    print(df.iloc[0][metrics].round(3).to_string())

    print("\nLatency percentiles (ms):")
    print(df[metrics].quantile([0.50, 0.95, 0.99]).round(3).to_string())
