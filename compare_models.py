import csv
import os

MODELS_FOLDER = "benchmark/models"

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

    values = [float(value) for value in values]

    if not values:
        return 0

    return sum(values) / len(values)


print()
print("=" * 70)
print("                 ⚡ THUNDERBOLT.AI")
print("                  MODEL COMPARISON")
print("=" * 70)


results = {}


for model_name, files in MODELS.items():

    benchmark_data = read_csv(files["benchmark"])
    quality_data = read_csv(files["quality"])

    response_times = [
        row["response_time"]
        for row in benchmark_data
    ]

    tokens_per_second = [
        row["tokens_per_second"]
        for row in benchmark_data
    ]

    cpu_average = [
        row["cpu_average"]
        for row in benchmark_data
    ]

    ram_average = [
        row["ram_average_gb"]
        for row in benchmark_data
    ]

    gpu_average = [
        row["gpu_average"]
        for row in benchmark_data
    ]

    vram_average = [
        row["vram_average_gb"]
        for row in benchmark_data
    ]

    quality_scores = [
        row["quality_score"]
        for row in quality_data
    ]

    results[model_name] = {

        "quality": average(quality_scores),

        "response_time": average(response_times),

        "tokens_per_second": average(tokens_per_second),

        "cpu": average(cpu_average),

        "ram": average(ram_average),

        "gpu": average(gpu_average),

        "vram": average(vram_average)
    }


print("\nMODEL PERFORMANCE")
print("-" * 70)

print(
    f"{'Model':<25}"
    f"{'Quality':>10}"
    f"{'Time':>12}"
    f"{'Tok/s':>12}"
    f"{'VRAM':>10}"
)

print("-" * 70)


for model, data in results.items():

    print(
        f"{model:<25}"
        f"{data['quality']:>9.2f}"
        f"{data['response_time']:>11.2f}s"
        f"{data['tokens_per_second']:>11.2f}"
        f"{data['vram']:>9.2f}GB"
    )


print("-" * 70)


best_quality = max(
    results,
    key=lambda model: results[model]["quality"]
)

best_speed = max(
    results,
    key=lambda model: results[model]["tokens_per_second"]
)

lowest_latency = min(
    results,
    key=lambda model: results[model]["response_time"]
)

lowest_vram = min(
    results,
    key=lambda model: results[model]["vram"]
)


print("\n🏆 CATEGORY WINNERS")
print("-" * 70)

print(
    f"Best answer quality : {best_quality}"
)

print(
    f"Best generation speed : {best_speed}"
)

print(
    f"Lowest response time : {lowest_latency}"
)

print(
    f"Lowest VRAM usage : {lowest_vram}"
)


print("\n📊 HARDWARE USAGE")
print("-" * 70)

for model, data in results.items():

    print(f"\n{model}")

    print(
        f"CPU average : {data['cpu']:.2f}%"
    )

    print(
        f"RAM average : {data['ram']:.2f} GB"
    )

    print(
        f"GPU average : {data['gpu']:.2f}%"
    )

    print(
        f"VRAM average : {data['vram']:.2f} GB"
    )


print("\n" + "=" * 70)
print("                    THUNDERBOLT.AI")
print("                  COMPARISON COMPLETE")
print("=" * 70)