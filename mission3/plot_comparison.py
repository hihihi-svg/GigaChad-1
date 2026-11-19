import matplotlib.pyplot as plt

labels = [
    "Remote Keep-Alive",
    "Remote No-Keep-Alive",
    "Localhost"
]

latencies = [17.70, 47.03, 4.89]

plt.figure(figsize=(9, 5))

bars = plt.bar(labels, latencies)

plt.ylabel("Average Round-Trip Latency (ms)")
plt.title("API Latency Comparison")
plt.grid(axis="y", alpha=0.3)

for bar, value in zip(bars, latencies):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.8,
        f"{value:.2f} ms",
        ha="center"
    )

plt.tight_layout()
plt.savefig("mission3/plots/latency_comparison.png", dpi=200)
plt.show()
