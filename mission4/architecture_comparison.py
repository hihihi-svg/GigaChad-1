widths = [32, 128, 256, 512, 2048]

SRAM = 300 * 1024
PSRAM = 8 * 1024 * 1024

print(f"{'Width':>8} {'Params':>12} {'F32 KB':>12} {'INT8 KB':>12} {'MACs':>14}")
print("-" * 65)

for w in widths:
    params = w*w + 8*w + 1
    f32 = params * 4
    int8 = params
    macs = w*w + 6*w

    print(
        f"{w:>8} {params:>12,} "
        f"{f32/1024:>12.2f} {int8/1024:>12.2f} "
        f"{macs:>14,}"
    )
