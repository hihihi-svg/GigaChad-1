
import matplotlib.pyplot as plt

architectures = [
    "4", "8", "16", "32", "64",
    "4,4", "8,8", "16,16", "32,32", "64,64"
]

parameters = [29, 57, 113, 225, 449, 49, 129, 385, 1281, 4609]

validation_mae = [
    24.05, 24.00, 24.03, 14.66, 24.01,
    13.34, 8.73, 8.53, 6.48, 6.73
]

plt.figure(figsize=(10, 6))
plt.scatter(parameters, validation_mae)

for i, architecture in enumerate(architectures):
    plt.annotate(
        architecture,
        (parameters[i], validation_mae[i]),
        xytext=(5, 5),
        textcoords="offset points"
    )

plt.xscale("log")
plt.xlabel("Number of Trainable Parameters (log scale)")
plt.ylabel("Validation MAE (days)")
plt.title("Network Size vs Validation Error")
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "/workspaces/GigaChad-1/mission2/mission2_comparison.png",
    dpi=300
)

plt.show()
