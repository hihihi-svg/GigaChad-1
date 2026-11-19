
import csv
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
BENCH = ROOT / "client" / "bench.py"
OUTPUT = ROOT / "mission3" / "benchmarks"
README = ROOT / "mission3" / "results.md"

PUBLIC_URL = (
    "https://cautious-space-trout-4qqvwwx44q7c754r-8000.app.github.dev"
)

OUTPUT.mkdir(parents=True, exist_ok=True)

TESTS = [
    ("Remote Keep-Alive", "remote_keepalive.csv",
     PUBLIC_URL, []),
    ("Remote No-Keep-Alive", "remote_no_keepalive.csv",
     PUBLIC_URL, ["--no-keepalive"]),
    ("Codespaces Localhost", "localhost.csv",
     "http://localhost:8000", []),
]

START_MARKER = "<!-- MISSION3_RESULTS_START -->"
END_MARKER = "<!-- MISSION3_RESULTS_END -->"


def percentile(values, p):
    values = sorted(values)
    if len(values) == 1:
        return values[0]

    position = (len(values) - 1) * p / 100
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    fraction = position - lower

    return values[lower] + (
        values[upper] - values[lower]
    ) * fraction


def run_benchmark(name, filename, url, extra_args):
    print(f"\n{'=' * 55}")
    print(f"Running: {name}")
    print("=" * 55)

    before = set(ROOT.glob("bench_*.csv"))

    command = [
        sys.executable,
        str(BENCH),
        "--url", url,
        "--n", "200",
        *extra_args,
    ]

    subprocess.run(command, cwd=ROOT, check=True)

    generated = list(set(ROOT.glob("bench_*.csv")) - before)

    if not generated:
        raise RuntimeError(
            f"No new benchmark CSV found for {name}"
        )

    latest = max(generated, key=os.path.getmtime)

    destination = OUTPUT / filename
    os.replace(latest, destination)

    with destination.open(newline="") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise RuntimeError(f"{filename} contains no data")

    numeric_columns = {}

    for column in rows[0]:
        if column == "i":
            continue
        values = []

        for row in rows:
            try:
                values.append(float(row[column]))
            except (ValueError, TypeError, KeyError):
                continue

        if values:
            numeric_columns[column] = values

    print(f"Saved: {destination.relative_to(ROOT)}")
    print(f"Requests: {len(rows)}")

    for column, values in numeric_columns.items():
        print(
            f"{column:24} "
            f"avg={sum(values)/len(values):.3f} "
            f"p50={percentile(values, 50):.3f} "
            f"p95={percentile(values, 95):.3f} "
            f"p99={percentile(values, 99):.3f} ms"
        )

    return {
        "name": name,
        "rows": len(rows),
        "columns": numeric_columns,
    }


def build_readme_section(results):
    now = datetime.now().astimezone().strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )

    lines = [
        START_MARKER,
        "## Latest Mission 3 Benchmark Results",
        "",
        f"**Last updated:** {now}",
        "",
        "All three benchmark runs were initiated from GitHub Codespaces. "
        "Remote tests use the public Codespaces URL; localhost tests use "
        "`http://localhost:8000`.",
        "",
    ]

    for result in results:
        lines.extend([
            f"### {result['name']}",
            "",
            f"Requests: {result['rows']}",
            "",
            "| Metric | Average (ms) | p50 (ms) | p95 (ms) | p99 (ms) |",
            "|---|---:|---:|---:|---:|",
        ])

        for column, values in result["columns"].items():
            avg = sum(values) / len(values)
            lines.append(
                f"| {column} | {avg:.3f} | "
                f"{percentile(values, 50):.3f} | "
                f"{percentile(values, 95):.3f} | "
                f"{percentile(values, 99):.3f} |"
            )

        lines.append("")

    lines.extend([
        "Benchmark results vary with network conditions and server load.",
        END_MARKER,
    ])

    return "\n".join(lines)


def update_readme(results):
    content = README.read_text(encoding="utf-8") if README.exists() else ""

    if START_MARKER in content and END_MARKER in content:
        start = content.index(START_MARKER)
        end = content.index(END_MARKER) + len(END_MARKER)

        updated = (
            content[:start]
            + build_readme_section(results)
            + content[end:]
        )
    else:
        updated = (
            content.rstrip()
            + "\n\n"
            + build_readme_section(results)
            + "\n"
        )

    README.write_text(updated, encoding="utf-8")
    print("\nmission3/results.md updated successfully.")
def main():
    results = []

    for test in TESTS:
        results.append(run_benchmark(*test))

    update_readme(results)

    print("\nAll benchmarks completed.")
    print("CSV files replaced and README results refreshed.")


if __name__ == "__main__":
    main()
