# Mission 4: ESP32-S3 Inference-Time Estimates

## Hardware
- Board: ESP32-S3
- CPU frequency: 240 MHz
- Model architecture: 5 -> 32 -> 32 -> 1
- Actual measured inference time at width 32: 37 microseconds

## Estimation methodology

The width-32 model provides the hardware measurement baseline.

For larger widths, inference time is estimated proportionally
to the number of multiply-accumulate operations (MACs).

Formula:

Estimated time = 37 * (MACs at width w / 1216)

Assumption: approximately constant MAC throughput.

These are analytical estimates, not measured hardware results.
They do not account for memory/cache effects or changes in
execution overhead at larger widths.

## Results

| Width | Architecture | Parameters | MACs | Estimated time |
|---:|---|---:|---:|---:|
| 32 | 5->32->32->1 | 1281 | 1216 | 37 us (measured) |
| 128 | 5->128->128->1 | 17409 | 17152 | 521.89 us (estimated) |
| 256 | 5->256->256->1 | 67585 | 67072 | 2.04 ms (estimated) |
| 512 | 5->512->512->1 | 266241 | 265216 | 8.07 ms (estimated) |
| 2048 | 5->2048->2048->1 | 4210689 | 4206592 | 128.00 ms (estimated) |

## Interpretation

The selected width-32 model has a small computational cost and
low measured inference latency on the ESP32-S3.

Larger widths increase computational requirements substantially.
The estimates are useful for comparison but should not be treated
as actual device benchmarks.
