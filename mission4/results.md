cat > mission4/results.md <<'EOF'
# Mission 4 – Edge AI Feasibility

## SRAM Cutoff Analysis

SRAM budget: 300 KB = 307,200 bytes

| Precision | Largest fitting width | Memory used | Next width |
|---|---:|---:|---:|
| Float32 | 273 | 306,856 bytes | 274 |
| INT8 | 550 | 306,901 bytes | 551 |

The INT8 representation allows a significantly wider network
within the same parameter-storage budget.

Note: These calculations include weights and biases only.
They do not represent complete runtime SRAM requirements.
EOF