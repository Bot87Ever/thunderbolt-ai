import csv
import os

import matplotlib.pyplot as plt

MODELS_FOLDER = "benchmark/models"
GRAPH_FOLDER = "benchmark/graphs"

os.makedirs(GRAPH_FOLDER, exist_ok=True)

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


results = {}


for model, files in MODELS.items():

    benchmark = read_csv(files["benchmark"])
    quality = read_csv(files["quality"])

    results[model] = {
        "quality": sum(
            float(row["quality_score"])
            for row in quality
        ) / len(quality),

        "response_time": sum(
            float(row["response_time"])
            for row in benchmark
        ) / len(benchmark),

        "tokens_per_second": sum(
            float(row["tokens_per_second"])
            for row in benchmark
        ) / len(benchmark),

        "cpu": sum(
            float(row["cpu_average"])
            for row in benchmark
        ) / len(benchmark),

        "ram": sum(
            float(row["ram_average_gb"])
            for row in benchmark
        ) / len(benchmark),

        "gpu": sum(
            float(row["gpu_average"])
            for row in benchmark
        ) / len(benchmark),

        "vram": sum(
            float(row["vram_average_gb"])
            for row in benchmark
        ) / len(benchmark)
    }


model_names = list(results.keys())


def create_graph(title, values, ylabel, filename):

    plt.figure(figsize=(10, 6))

    plt.bar(model_names, values)

    plt.title(title)

    plt.ylabel(ylabel)

    plt.xticks(rotation=15)

    plt.tight_layout()

    path = os.path.join(GRAPH_FOLDER, filename)

    plt.savefig(path, dpi=200)

    plt.close()

    print(f"Created: {path}")


create_graph(
    "Thunderbolt.ai - Answer Quality",
    [
        results[model]["quality"]
        for model in model_names
    ],
    "Quality Score / 10",
    "quality_comparison.png"
)


create_graph(
    "Thunderbolt.ai - Response Time",
    [
        results[model]["response_time"]
        for model in model_names
    ],
    "Seconds",
    "response_time_comparison.png"
)


create_graph(
    "Thunderbolt.ai - Generation Speed",
    [
        results[model]["tokens_per_second"]
        for model in model_names
    ],
    "Tokens / Second",
    "tokens_per_second_comparison.png"
)


create_graph(
    "Thunderbolt.ai - CPU Usage",
    [
        results[model]["cpu"]
        for model in model_names
    ],
    "CPU Usage %",
    "cpu_comparison.png"
)


create_graph(
    "Thunderbolt.ai - RAM Usage",
    [
        results[model]["ram"]
        for model in model_names
    ],
    "RAM GB",
    "ram_comparison.png"
)


create_graph(
    "Thunderbolt.ai - GPU Usage",
    [
        results[model]["gpu"]
        for model in model_names
    ],
    "GPU Usage %",
    "gpu_comparison.png"
)


create_graph(
    "Thunderbolt.ai - VRAM Usage",
    [
        results[model]["vram"]
        for model in model_names
    ],
    "VRAM GB",
    "vram_comparison.png"
)


print()
print("=" * 60)
print("⚡ THUNDERBOLT.AI")
print("GRAPH GENERATION COMPLETE")
print("=" * 60)

print()
print("Graphs saved in:")
print(GRAPH_FOLDER)