"""
app/main.py -- STARTER battery API. Look for TODO.

    uvicorn app.main:app --host 0.0.0.0 --port 8000

GET  /health          -> {"status": "ok", "team": 7, "params": 1281, "val_mae": 3.4}
GET  /model_info      -> the per-layer table: params, bytes, MACs, and whether it fits the doorbell
POST /predict         one reading  -> {"days_left": 52.1, "timings_ms": {...}}
POST /predict_batch   {"rows": [reading, ...]} -> {"days_left": [...], "timings_ms": {...}}
A reading that is out of range gets HTTP 422 with the reason, never a guess.
"""
import json
import time

import numpy as np
import torch
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from app.model import FEATURES, BatteryNet

cfg = json.load(open("model/config.json"))
net = BatteryNet(tuple(cfg["hidden"]))
net.load_state_dict(torch.load("model/model.pt", weights_only=True))
net.eval()
torch.set_num_threads(1)
MU, SD = np.array(cfg["mu"], np.float32), np.array(cfg["sd"], np.float32)
N_PARAMS = sum(p.numel() for p in net.parameters())


class Reading(BaseModel):
    # TODO Mission 3: a doorbell will send you glitches like the ones you found in Mission 1.
    # Give every field a sensible range, e.g. Field(ge=..., le=...), so a glitch is refused
    # with HTTP 422 instead of being answered with a made-up number. Base the limits on what a
    # real sensor can report, not on your data's min and max: real readings must still get answers.


    # Validate sensor readings against physically plausible operating ranges.
    battery_v: float = Field(ge=0.0, le=5.5)
    temp_c: float = Field(ge=-40.0, le=85.0)
    rings_per_day: float = Field(ge=0.0, le=500.0)
    wifi_rssi_dbm: float = Field(ge=-100.0, le=0.0)
    age_months: float = Field(ge=0.0, le=120.0)

class Batch(BaseModel):
    rows: list[Reading] = Field(min_length=1, max_length=10000)


app = FastAPI(title="Doorbell battery API")
ms = lambda t0: round((time.perf_counter() - t0) * 1000, 3)




@app.get("/model_info")
def model_info():
    # TODO Mission 2 + 4: return your per-layer table, worked out FROM THE NETWORK (net.net),
    # not typed in by hand, so it stays right if you change the layer sizes.
    #
    # Required original keys:
    # {"layers": [{"name": "linear1", "in": 5, "out": 32,
    #              "params": ..., "bytes_f32": ..., "macs": ...}, ...],
    #  "total_params": ..., "total_bytes_f32": ...,
    #  "total_bytes_int8": ..., "total_macs": ...,
    #  "fits_300kb_sram_f32": true/false,
    #  "fits_300kb_sram_int8": true/false}
    #
    # Count only the Linear layers (ReLU has no parameters).
    # Clue: a Linear layer m has m.in_features and m.out_features.

    # This part actually inspects the NN and gives the size,
    # computational cost, etc.

    layers = []
    linear_layers = []

    # Find all Linear layers dynamically from the trained network.
    for module in net.net.modules():
        if isinstance(module, torch.nn.Linear):
            linear_layers.append(module)

    # Calculate parameter count, storage and MACs for each layer.
    for i, module in enumerate(linear_layers):
        in_features = module.in_features
        out_features = module.out_features

        params = module.weight.numel()

        if module.bias is not None:
            params += module.bias.numel()

        layers.append({
            "name": f"linear{i + 1}",
            "in": in_features,
            "out": out_features,
            "params": params,
            "bytes_f32": params * 4,
            "macs": in_features * out_features
        })

    # Total number of trainable parameters across all Linear layers.
    total_params = sum(layer["params"] for layer in layers)

    # Float32 uses 4 bytes per parameter.
    total_bytes_f32 = total_params * 4

    # Assumption: all weights and biases are represented using INT8.
    # This is an idealized storage estimate, not actual quantized inference.
    total_bytes_int8 = total_params

    # Total Multiply-Accumulate operations for one inference.
    total_macs = sum(layer["macs"] for layer in layers)

    # ---------------------------------------------------------
    # Mission 4: Activation memory calculations
    # ---------------------------------------------------------

    # Largest hidden-layer activation for a single input.
    # The final Linear layer is excluded because it is the output layer.
    hidden_widths = [
        layer.out_features for layer in linear_layers[:-1]
    ]

    max_activation_elements = max(hidden_widths, default=0)

    # Memory occupied by the largest individual hidden activation.
    activation_bytes_f32 = max_activation_elements * 4
    activation_bytes_int8 = max_activation_elements

    # Calculate total working activation buffers.
    # Our Arduino implementation stores:
    # - Normalized input array
    # - First hidden-layer array (h1)
    # - Second hidden-layer array (h2)
    # - Final output value
    #
    # This is a conservative buffer estimate for the current implementation.
    input_elements = linear_layers[0].in_features if linear_layers else 0
    output_elements = linear_layers[-1].out_features if linear_layers else 0

    peak_activation_elements = (
        input_elements
        + sum(hidden_widths)
        + output_elements
    )

    peak_activation_bytes_f32 = peak_activation_elements * 4
    peak_activation_bytes_int8 = peak_activation_elements

    # ---------------------------------------------------------
    # Mission 4: ESP32-S3 memory budgets
    # ---------------------------------------------------------

    # Assignment hardware budgets:
    # SRAM budget = 300 KB
    # PSRAM capacity = 8 MB
    sram_limit = 300 * 1024
    psram_limit = 8 * 1024 * 1024

    # Check whether model weights alone fit into SRAM.
    fits_sram_weights_f32 = total_bytes_f32 <= sram_limit
    fits_sram_weights_int8 = total_bytes_int8 <= sram_limit

    # Check whether weights plus activation buffers fit into SRAM.
    # Runtime overhead, stack, heap and other allocations are excluded.
    fits_sram_f32 = (
        total_bytes_f32 + peak_activation_bytes_f32 <= sram_limit
    )

    fits_sram_int8 = (
        total_bytes_int8 + peak_activation_bytes_int8 <= sram_limit
    )

    # Check whether model weights fit into PSRAM.
    fits_psram_f32 = total_bytes_f32 <= psram_limit
    fits_psram_int8 = total_bytes_int8 <= psram_limit

    # Check whether weights plus activation buffers fit into PSRAM.
    fits_psram_f32_with_activations = (
        total_bytes_f32 + peak_activation_bytes_f32 <= psram_limit
    )

    fits_psram_int8_with_activations = (
        total_bytes_int8 + peak_activation_bytes_int8 <= psram_limit
    )

    return {
        # Original Mission 2 layer-by-layer information.
        "layers": layers,
        "total_params": total_params,
        "total_bytes_f32": total_bytes_f32,
        "total_bytes_int8": total_bytes_int8,
        "total_macs": total_macs,

        # Mission 4: largest individual activation.
        "activation_elements": max_activation_elements,
        "activation_bytes_f32": activation_bytes_f32,
        "activation_bytes_int8": activation_bytes_int8,

        # Mission 4: total working activation buffers.
        "peak_activation_elements": peak_activation_elements,
        "peak_activation_bytes_f32": peak_activation_bytes_f32,
        "peak_activation_bytes_int8": peak_activation_bytes_int8,

        # Original required SRAM feasibility keys.
        "fits_300kb_sram_f32": fits_sram_f32,
        "fits_300kb_sram_int8": fits_sram_int8,

        # Additional weight-only SRAM feasibility.
        "fits_300kb_sram_weights_only_f32": fits_sram_weights_f32,
        "fits_300kb_sram_weights_only_int8": fits_sram_weights_int8,

        # Mission 4: PSRAM feasibility.
        "fits_8mb_psram_f32": fits_psram_f32,
        "fits_8mb_psram_int8": fits_psram_int8,
        "fits_8mb_psram_f32_with_activations": fits_psram_f32_with_activations,
        "fits_8mb_psram_int8_with_activations": fits_psram_int8_with_activations,

        # Document the assumptions behind the calculations.
        "memory_assumptions": {
            "sram_budget_bytes": sram_limit,
            "psram_budget_bytes": psram_limit,
            "float32_bytes_per_parameter": 4,
            "int8_bytes_per_parameter": 1,
            "int8_bias_assumption": "Biases also counted as 1 byte",
            "fit_scope": (
                "Weights plus input, hidden and output working buffers; "
                "excludes runtime overhead"
            )
        }
    }

@app.get("/health")
def health():
    return {"status": "ok", "team": cfg["team"], "params": N_PARAMS, "val_mae": cfg["val_mae"]}


async def run(request: Request, schema):
    t_all = time.perf_counter()
    t = {}

    t0 = time.perf_counter()
    try:
        data = schema.model_validate_json(await request.body())
    except ValidationError as e:
        return JSONResponse(status_code=422, content={
            "error": "bad reading",
            "detail": json.loads(e.json())
        })
    t["parse"] = ms(t0)

    rows = data.rows if isinstance(data, Batch) else [data]
     # TODO Mission 3: time each of the three stages below the same way "parse" is timed above,
    # storing them as t["normalise"], t["inference"] and t["build"].

    t0 = time.perf_counter()
    x = (np.array([[getattr(r, f) for f in FEATURES] for r in rows],
                  np.float32) - MU) / SD
    t["normalise"] = ms(t0)

    t0 = time.perf_counter()
    with torch.no_grad():
        y = net(torch.from_numpy(x)).numpy()
    t["inference"] = ms(t0)

    t0 = time.perf_counter()
    days = [round(float(v), 2) for v in np.maximum(y, 0)]
    body = {"days_left": days if isinstance(data, Batch) else days[0]}
    t["build"] = ms(t0)

    t["server_total"] = ms(t_all)
    body["timings_ms"] = t
    return body

@app.post("/predict")
async def predict(request: Request, reading: Reading):
    return await run(request, Reading)


@app.post("/predict_batch")
async def predict_batch(request: Request, batch: Batch):
    return await run(request, Batch)
