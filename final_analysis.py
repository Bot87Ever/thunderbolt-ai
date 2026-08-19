import csv
import os

MODELS_FOLDER = "benchmark/models"
OUTPUT_FILE = "benchmark/final_analysis.csv"

MODELS = {
    "Qwen2.5-Coder 7B": {
        "benchmark": "qwen2.5-coder-7b.csv",
        "quality": "qwen2.5-coder-7b-quality.csv"
    },
    "Gemma 3 4B": {
        "benchmark": "gemma3-4b.csv",
        "quality": "gemma3-4b-quality.csv"
    },
    "Qwen3 8B": {
        "benchmark": "qwen3-8b.csv",
        "quality": "qwen3-8b-quality.csv"
    }
}


def read_csv(filename):

    path = os.path.join(MODELS_FOLDER, filename)

    with open(path, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def average(values):

    if not values:
        return 0

    return sum(values) / len(values)


results = {}


for model, files in MODELS.items():

    benchmark_data = read_csv(files["benchmark"])
    quality_data = read_csv(files["quality"])

    response_time = average([
        float(row["response_time"])
        for row in benchmark_data
    ])

    tokens_per_second = average([
        float(row["tokens_per_second"])
        for row in benchmark_data
    ])

    cpu = average([
        float(row["cpu_average"])
        for row in benchmark_data
    ])

    ram = average([
        float(row["ram_average_gb"])
        for row in benchmark_data
    ])

    gpu = average([
        float(row["gpu_average"])
        for row in benchmark_data
    ])

    vram = average([
        float(row["vram_average_gb"])
        for row in benchmark_data
    ])

    quality = average([
        float(row["quality_score"])
        for row in quality_data
    ])

    results[model] = {
        "quality": quality,
        "response_time": response_time,
        "tokens_per_second": tokens_per_second,
        "cpu": cpu,
        "ram": ram,
        "gpu": gpu,
        "vram": vram
    }


# --------------------------------------------------
# NORMALIZATION
# --------------------------------------------------

max_quality = max(
    data["quality"]
    for data in results.values()
)

max_speed = max(
    data["tokens_per_second"]
    for data in results.values()
)

min_response = min(
    data["response_time"]
    for data in results.values()
)

min_cpu = min(
    data["cpu"]
    for data in results.values()
)

min_ram = min(
    data["ram"]
    for data in results.values()
)

min_gpu = min(
    data["gpu"]
    for data in results.values()
)

min_vram = min(
    data["vram"]
    for data in results.values()
)


# --------------------------------------------------
# FINAL SCORE
# --------------------------------------------------

for model, data in results.items():

    quality_score = (
        data["quality"] / max_quality
    ) * 100

    speed_score = (
        data["tokens_per_second"] / max_speed
    ) * 100

    response_score = (
        min_response / data["response_time"]
    ) * 100

    cpu_score = (
        min_cpu / data["cpu"]
    ) * 100

    ram_score = (
        min_ram / data["ram"]
    ) * 100

    gpu_score = (
        min_gpu / data["gpu"]
    ) * 100

    vram_score = (
        min_vram / data["vram"]
    ) * 100

    hardware_score = (
        cpu_score +
        ram_score +
        gpu_score +
        vram_score
    ) / 4

    final_score = (
        quality_score * 0.40 +
        speed_score * 0.25 +
        response_score * 0.15 +
        hardware_score * 0.20
    )

    data["quality_score_normalized"] = quality_score
    data["speed_score"] = speed_score
    data["response_score"] = response_score
    data["hardware_score"] = hardware_score
    data["final_score"] = final_score


# --------------------------------------------------
# RANKING
# --------------------------------------------------

ranking = sorted(
    results.items(),
    key=lambda item: item[1]["final_score"],
    reverse=True
)


print()
print("=" * 75)
print("                 ⚡ THUNDERBOLT.AI")
print("                    FINAL ANALYSIS")
print("=" * 75)

print()
print("OVERALL MODEL RANKING")
print("-" * 75)

print(
    f"{'Rank':<8}"
    f"{'Model':<25}"
    f"{'Quality':>10}"
    f"{'Speed':>10}"
    f"{'Hardware':>12}"
    f"{'FINAL':>10}"
)

print("-" * 75)


for rank, (model, data) in enumerate(ranking, start=1):

    print(
        f"{rank:<8}"
        f"{model:<25}"
        f"{data['quality']:>9.2f}"
        f"{data['tokens_per_second']:>9.2f}"
        f"{data['hardware_score']:>11.2f}"
        f"{data['final_score']:>9.2f}"
    )


print("-" * 75)


winner = ranking[0][0]

print()
print("🏆 OVERALL WINNER")
print(f"   {winner}")


# --------------------------------------------------
# CATEGORY WINNERS
# --------------------------------------------------

best_quality = max(
    results,
    key=lambda model: results[model]["quality"]
)

best_speed = max(
    results,
    key=lambda model: results[model]["tokens_per_second"]
)

best_response = min(
    results,
    key=lambda model: results[model]["response_time"]
)

best_vram = min(
    results,
    key=lambda model: results[model]["vram"]
)

best_cpu = min(
    results,
    key=lambda model: results[model]["cpu"]
)


print()
print("CATEGORY WINNERS")
print("-" * 75)

print(f"Best quality       : {best_quality}")
print(f"Fastest generation : {best_speed}")
print(f"Lowest latency     : {best_response}")
print(f"Lowest VRAM        : {best_vram}")
print(f"Lowest CPU usage   : {best_cpu}")


# --------------------------------------------------
# MODEL RECOMMENDATIONS
# --------------------------------------------------

print()
print("THUNDERBOLT.AI RECOMMENDATIONS")
print("-" * 75)

print(
    "Best overall model : "
    + winner
)

print(
    "Best coding model  : "
    "Qwen2.5-Coder 7B"
)

print(
    "Best general model : "
    "Gemma 3 4B"
)

print(
    "Largest model      : "
    "Qwen3 8B"
)


# --------------------------------------------------
# SAVE FINAL RESULTS
# --------------------------------------------------

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "rank",
        "model",
        "quality",
        "response_time",
        "tokens_per_second",
        "cpu_average",
        "ram_average_gb",
        "gpu_average",
        "vram_average_gb",
        "quality_score_normalized",
        "speed_score",
        "response_score",
        "hardware_score",
        "final_score"
    ])

    for rank, (model, data) in enumerate(
        ranking,
        start=1
    ):

        writer.writerow([
            rank,
            model,
            round(data["quality"], 2),
            round(data["response_time"], 2),
            round(data["tokens_per_second"], 2),
            round(data["cpu"], 2),
            round(data["ram"], 2),
            round(data["gpu"], 2),
            round(data["vram"], 2),
            round(data["quality_score_normalized"], 2),
            round(data["speed_score"], 2),
            round(data["response_score"], 2),
            round(data["hardware_score"], 2),
            round(data["final_score"], 2)
        ])


print()
print("=" * 75)
print("Final results saved to:")
print(OUTPUT_FILE)
print("=" * 75)