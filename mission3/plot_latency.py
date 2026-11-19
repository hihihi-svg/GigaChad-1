import matplotlib.pyplot as plt

labels = ["Remote (Keep-Alive)", "Localhost"]

server = [0.317, 0.231]
overhead = [17.70 - 0.317, 4.890 - 0.231]

fig, ax = plt.subplots(figsize=(9, 5))

ax.barh(labels, server, label="Server processing")
ax.barh(labels, overhead, left=server, label="Network/framework overhead")

ax.set_xlabel("Average latency (ms)")
ax.set_title("API Latency Breakdown")
ax.legend()
ax.grid(axis="x", alpha=0.3)

for i in range(len(labels)):
    ax.text(server[i] + overhead[i] / 2, i,
            f"{overhead[i]:.2f} ms", ha="center", va="center")

plt.tight_layout()
plt.savefig("mission3/plots/latency_breakdown.png", dpi=200)
plt.show()
