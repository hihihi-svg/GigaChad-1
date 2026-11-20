
SRAM = 300 * 1024

for precision, bytes_per_param in [("Float32", 4), ("INT8", 1)]:
    largest_fit = 0

    for w in range(1, 10000):
        params = w*w + 8*w + 1
        required = params * bytes_per_param

        if required <= SRAM:
            largest_fit = w
        else:
            break

    params = largest_fit**2 + 8*largest_fit + 1
    used = params * bytes_per_param

    print(f"{precision}:")
    print(f"  Largest fitting width: {largest_fit}")
    print(f"  Memory used: {used:,} bytes")
    print(f"  Next width: {largest_fit + 1}")
    print()
