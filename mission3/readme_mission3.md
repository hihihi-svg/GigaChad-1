## Mission 3 – API Benchmarking

This module measures API performance under three execution conditions:

1. **Remote Keep-Alive:** Laptop to GitHub Codespaces API using a persistent HTTP connection.
2. **Remote No-Keep-Alive:** Laptop to GitHub Codespaces API using a new connection for each request.
3. **Localhost:** Benchmark client and API running inside the Codespace.

### Prerequisites

- Python dependencies installed from `requirements.txt`.
- FastAPI server running on port `8000`.
- Codespaces port `8000` set to **Public** for remote benchmarking.
- The benchmark client at `client/bench.py`.

### Refreshing benchmark results

The benchmark refresh script runs 200 requests per test, calculates latency statistics, and replaces the previous CSV instead of accumulating multiple files.

**1. Run remote benchmarks from your laptop terminal:**

```bash
python mission3/refresh_benchmark.py remote
```

This runs:
- Remote Keep-Alive
- Remote No-Keep-Alive

**2. Run the localhost benchmark from the Codespaces terminal:**

Make sure the API server is running:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then execute:

```bash
python mission3/refresh_benchmark.py local
```

This runs the localhost benchmark.

### Output files

The latest benchmark results are stored in:

```text
mission3/
├── benchmarks/
│   ├── remote_keepalive.csv
│   ├── remote_no_keepalive.csv
│   └── localhost.csv
└── refresh_benchmark.py
```

Existing CSV files are overwritten on subsequent runs.

### Metrics

The script displays the following statistics for each numeric benchmark column:

- **Average:** Mean measured latency.
- **p50:** Median latency; 50% of requests complete within this time.
- **p95:** 95% of requests complete within this time.
- **p99:** 99% of requests complete within this time.

The benchmark measures client round-trip latency and server-side stages, including parsing, normalisation, inference, and response construction.

### Visualisation

The latency breakdown and comparison plots are maintained separately in `mission3/plots/`. They are supporting visualisations and do not need to be regenerated for every benchmark run.

**Note:** Benchmark results can vary with network conditions, server load, and connection setup overhead. The latest CSV measurements should be used when analysing performance.