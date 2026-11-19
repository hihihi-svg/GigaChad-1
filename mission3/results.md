# Mission 3 – API Performance Benchmarking and Latency Analysis

## 1. Remote API Latency: Keep-Alive vs No-Keep-Alive

We benchmarked 200 requests from the laptop to the FastAPI application hosted on GitHub Codespaces to understand the impact of HTTP connection reuse.

### 1.1 Benchmark Results

| Metric | Keep-Alive | No-Keep-Alive |
|---|---:|---:|
| Average latency | 17.70 ms | 47.03 ms |
| p50 latency | 11.85 ms | 40.82 ms |
| p95 latency | 23.93 ms | 68.17 ms |
| p99 latency | 152.62 ms | 172.81 ms |
| Average server processing | 0.317 ms | 0.356 ms |

### 1.2 Observation

Keep-alive reuses an existing HTTP connection for multiple requests, whereas no-keep-alive establishes a new connection for each request.

- Keep-alive average latency: 17.70 ms.
- No-keep-alive average latency: 47.03 ms.
- Connection reuse reduced average latency by approximately **62.4%**.

This demonstrates that reusing HTTP connections reduces connection overhead and improves API response time.

## 2. Localhost Performance Benchmark

We executed the benchmark from inside GitHub Codespaces using `http://localhost:8000` to measure API performance without the external laptop-to-Codespaces network path.

### 2.1 Benchmark Results

| Metric | Average Latency |
|---|---:|
| Round-trip latency | 4.890 ms |
| Parse | 0.009 ms |
| Normalise | 0.028 ms |
| Inference | 0.162 ms |
| Build | 0.017 ms |
| Server total | 0.231 ms |
| Network/framework overhead | 4.659 ms |

### 2.2 Observation

Localhost achieved significantly lower latency because requests were sent directly within the Codespaces environment, avoiding the external network path and public port forwarding.

The server processing time was only 0.231 ms, while the remaining 4.659 ms was attributed to network and framework overhead.

## 3. Individual Requests vs Batch Processing

We compared processing 400 readings through separate `/predict` requests against processing all 400 readings through a single `/predict_batch` request.

### 3.1 Benchmark Results

| Approach | Total Time |
|---|---:|
| 400 individual `/predict` requests | 1617.08 ms |
| One `/predict_batch` request containing 400 readings | 11.78 ms |

**Batch processing speedup: 137.24×**

### 3.2 Observation

Batch processing was approximately **137 times faster** than sending 400 individual requests.

This improvement comes from reducing repeated HTTP request overhead and processing multiple readings together in a single inference operation.

The experiment demonstrates that batching can significantly improve API efficiency when handling multiple predictions.

## 4. Detailed Latency Analysis

To understand API performance more precisely, we measured the first request latency and calculated p50, p95 and p99 latency percentiles for all three configurations.

### 4.1 First Request and Round-Trip Latency Percentiles

| Metric | Remote Keep-Alive | Remote No-Keep-Alive | Localhost |
|---|---:|---:|---:|
| First request | 273.804 ms | 52.965 ms | 8.168 ms |
| p50 | 12.534 ms | 38.588 ms | 4.313 ms |
| p95 | 24.929 ms | 65.096 ms | 10.432 ms |
| p99 | 169.132 ms | 156.690 ms | 15.044 ms |

### 4.2 Server-Stage Latency Percentiles

The following table presents the p50 latency for each internal processing stage.

| Stage | Remote Keep-Alive | Remote No-Keep-Alive | Localhost |
|---|---:|---:|---:|
| Parse | 0.013 ms | 0.016 ms | 0.008 ms |
| Normalise | 0.035 ms | 0.044 ms | 0.022 ms |
| Inference | 0.203 ms | 0.233 ms | 0.130 ms |
| Build | 0.020 ms | 0.020 ms | 0.016 ms |
| Server total | 0.288 ms | 0.336 ms | 0.189 ms |

### 4.3 Observations

1. **Connection reuse:** Keep-alive achieved lower median and p95 latency than no-keep-alive by reusing established HTTP connections.
2. **First-request overhead:** The first remote keep-alive request took 273.804 ms, significantly higher than subsequent requests. This indicates substantial initial connection or forwarding overhead.
3. **Localhost performance:** Localhost achieved the lowest median latency because it avoids the external laptop-to-Codespaces network path.
4. **Server efficiency:** Internal server processing accounts for only a small fraction of the overall round-trip latency.
5. **Latency variability:** The p99 values reveal occasional slow requests even when typical response times are low.

These results demonstrate why API performance should be evaluated using latency percentiles in addition to average latency.

## 5. Overall Findings

The experiments demonstrate three important API performance improvements:

- **HTTP Keep-Alive:** Reduces repeated connection setup overhead and improves response time.
- **Localhost Execution:** Helps isolate the external network contribution to overall latency.
- **Batch Processing:** Significantly reduces repeated HTTP request overhead, achieving a measured 137.24× speedup for 400 readings.

Overall, the experiments show that API latency is influenced not only by model inference but also by HTTP communication, connection management, request processing and network overhead.

<!-- MISSION3_RESULTS_START -->
## Latest Mission 3 Benchmark Results

**Last updated:** 2026-11-19 20:16:28 UTC

All three benchmark runs were initiated from GitHub Codespaces. Remote tests use the public Codespaces URL; localhost tests use `http://localhost:8000`.

### Remote Keep-Alive

Requests: 200

| Metric | Average (ms) | p50 (ms) | p95 (ms) | p99 (ms) |
|---|---:|---:|---:|---:|
| i | 99.500 | 99.500 | 189.050 | 197.010 |
| round_trip | 17.301 | 10.938 | 26.820 | 145.896 |
| parse | 0.010 | 0.009 | 0.015 | 0.037 |
| normalise | 0.025 | 0.023 | 0.046 | 0.056 |
| inference | 0.154 | 0.135 | 0.212 | 0.562 |
| build | 0.015 | 0.015 | 0.020 | 0.041 |
| server_total | 0.216 | 0.196 | 0.298 | 0.659 |
| network_and_framework | 17.085 | 10.714 | 26.616 | 145.595 |

### Remote No-Keep-Alive

Requests: 200

| Metric | Average (ms) | p50 (ms) | p95 (ms) | p99 (ms) |
|---|---:|---:|---:|---:|
| i | 99.500 | 99.500 | 189.050 | 197.010 |
| round_trip | 42.604 | 40.447 | 56.802 | 63.123 |
| parse | 0.015 | 0.015 | 0.019 | 0.026 |
| normalise | 0.043 | 0.041 | 0.060 | 0.080 |
| inference | 0.238 | 0.216 | 0.297 | 1.311 |
| build | 0.020 | 0.019 | 0.027 | 0.051 |
| server_total | 0.334 | 0.305 | 0.419 | 1.402 |
| network_and_framework | 42.269 | 40.074 | 56.404 | 62.866 |

### Codespaces Localhost

Requests: 200

| Metric | Average (ms) | p50 (ms) | p95 (ms) | p99 (ms) |
|---|---:|---:|---:|---:|
| i | 99.500 | 99.500 | 189.050 | 197.010 |
| round_trip | 2.232 | 2.033 | 3.960 | 4.503 |
| parse | 0.008 | 0.008 | 0.009 | 0.029 |
| normalise | 0.023 | 0.021 | 0.033 | 0.052 |
| inference | 0.126 | 0.126 | 0.166 | 0.268 |
| build | 0.023 | 0.015 | 0.017 | 0.041 |
| server_total | 0.192 | 0.183 | 0.228 | 0.416 |
| network_and_framework | 2.040 | 1.846 | 3.735 | 4.316 |

Benchmark results vary with network conditions and server load.
<!-- MISSION3_RESULTS_END -->
