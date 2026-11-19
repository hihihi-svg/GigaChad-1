"""
train.py -- STARTER. Clean the data, fit baselines, train the network, save it for the server.

    python train.py --team 7 --hidden 32,32
Writes model/model.pt and model/config.json, which app/main.py loads.

Look for TODO. The training loop is given; the decisions are yours.
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
import torch

from app.model import FEATURES, BatteryNet

ap = argparse.ArgumentParser()
ap.add_argument("--team", type=int, required=True)
ap.add_argument("--hidden", default="32,32")
ap.add_argument("--epochs", type=int, default=1500)
a = ap.parse_args()
hidden = tuple(int(h) for h in a.hidden.split(","))

df = pd.read_csv(f"data/team_{a.team:02d}_train.csv")
# TODO Mission 1: find the sensor glitches (plot every column first!) and write a rule that
# marks them. Say in your report how many you found and why each rule is safe.
# Mission 1: Glitch detection
# -127°C is treated as an invalid temperature sensor reading.
bad = df["temp_c"] == -127

print(f"{len(df)} rows, {bad.sum()} glitch rows dropped")

df = df[~bad].copy()

rng = np.random.default_rng(0)
idx = rng.permutation(len(df)); n_val = len(df) // 5
val, tr = df.iloc[idx[:n_val]], df.iloc[idx[n_val:]]
X, y = tr[FEATURES].to_numpy(np.float32), tr.days_left.to_numpy(np.float32)
Xv, yv = val[FEATURES].to_numpy(np.float32), val.days_left.to_numpy(np.float32)
# TODO Mission 2: normalisation. Why must mu and sd come from the TRAINING rows only?
mu, sd = np.zeros(X.shape[1], np.float32), np.ones(X.shape[1], np.float32)

mae = lambda p, t: float(np.mean(np.abs(p - t)))
print(f"baseline (predict the mean): {mae(np.full_like(yv, y.mean()), yv):.2f} days")
# TODO Mission 1: a straight-line model (linear regression) as the second baseline.
# Mission 1: Linear regression baseline

X_train_aug = np.column_stack([X, np.ones(len(X))])
X_val_aug = np.column_stack([Xv, np.ones(len(Xv))])

weights, residuals, rank, singular_values = np.linalg.lstsq(
    X_train_aug, y, rcond=None
)

linear_predictions = X_val_aug @ weights

linear_mae = mae(linear_predictions, yv)

# Identify the largest linear regression prediction errors
errors = np.abs(linear_predictions - yv)

worst_indices = np.argsort(errors)[-10:][::-1]

print("\nTop 10 Linear Regression Prediction Errors:")
print("Actual Days | Predicted Days | Absolute Error")

for i in worst_indices:
    print(
        f"{yv[i]:11.2f} | "
        f"{linear_predictions[i]:14.2f} | "
        f"{errors[i]:14.2f}"
    )

print(f"baseline (linear regression): {linear_mae:.2f} days")
import matplotlib.pyplot as plt

plt.figure(figsize=(7, 5))
plt.scatter(yv, linear_predictions, alpha=0.6)
plt.xlabel("Actual days_left")
plt.ylabel("Predicted days_left")
plt.title("Linear Regression: Predicted vs Actual")
plt.plot(
    [yv.min(), yv.max()],
    [yv.min(), yv.max()],
    "r--"
)
plt.tight_layout()
plt.savefig("mission1/reports/linear_regression_plot.png")
plt.close()
# Use np.linalg.lstsq on [X, 1]. Print its validation MAE the same way as the line above.

torch.manual_seed(0)
net = BatteryNet(hidden)
opt = torch.optim.Adam(net.parameters(), lr=3e-3)
Xt, yt = torch.tensor((X - mu) / sd), torch.tensor(y)
Xvt = torch.tensor((Xv - mu) / sd)
for ep in range(a.epochs):
    perm = torch.randperm(len(Xt))
    for i in range(0, len(Xt), 128):
        b = perm[i:i + 128]
        loss = torch.nn.functional.mse_loss(net(Xt[b]), yt[b])
        opt.zero_grad(); loss.backward(); opt.step()
    if ep % 300 == 0 or ep == a.epochs - 1:
        with torch.no_grad():
            print(f"  epoch {ep:4d}  val MAE {mae(net(Xvt).numpy(), yv):.2f} days")
with torch.no_grad():
    val_mae = mae(net(Xvt).numpy(), yv)
print(f"network {hidden}:            {val_mae:.2f} days")

os.makedirs("model", exist_ok=True)
torch.save(net.state_dict(), "model/model.pt")
json.dump(dict(team=a.team, hidden=list(hidden), mu=mu.tolist(), sd=sd.tolist(),
               features=FEATURES, val_mae=round(val_mae, 2)), open("model/config.json", "w"), indent=2)
print("saved model/model.pt and model/config.json")
