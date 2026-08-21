import csv
import json
import os
import subprocess
import threading
import time
from datetime import datetime

import ollama
import psutil

MODEL = "gemma3:4b"

QUESTIONS_FILE = "benchmark/questions.json"
RESULTS_FILE = "benchmark/benchmark_results.csv"


def get_gpu_stats():
    try:
        result = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used,memory.total",
                "--format=csv,noheader,nounits"
            ],
            text=True
        )

        gpu_usage, vram_used, vram_total = result.strip().split(",")

        return (
            float(gpu_usage),
            float(vram_used),
            float(vram_total)
        )

    except Exception:
        return 0, 0, 0


def monitor_hardware(stop_event, samples):

    while not stop_event.is_set():

        cpu = psutil.cpu_percent(interval=0.1)

        ram = psutil.virtual_memory().used / (1024 ** 3)

        gpu, vram, vram_total = get_gpu_stats()

        samples.append({
            "cpu": cpu,
            "ram": ram,
            "gpu": gpu,
            "vram": vram,
            "vram_total": vram_total
        })


with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
    questions = json.load(file)


os.makedirs("benchmark", exist_ok=True)


with open(
    RESULTS_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "timestamp",
        "model",
        "question_id",
        "category",
        "question",
        "answer",
        "response_time",
        "generated_tokens",
        "tokens_per_second",
        "cpu_average",
        "cpu_peak",
        "ram_average_gb",
        "ram_peak_gb",
        "gpu_average",
        "gpu_peak",
        "vram_average_gb",
        "vram_peak_gb",
        "vram_total_gb"
    ])


print("\n  THUNDERBOLT.AI BENCHMARK")
print("=" * 60)
print(f"Model: {MODEL}")
print(f"Questions: {len(questions)}")
print("=" * 60)


for item in questions:

    question_id = item["id"]
    category = item["category"]
    question = item["question"]

    print(f"\n[{question_id}/{len(questions)}] {category}")
    print(f"Question: {question}")

    samples = []

    stop_event = threading.Event()

    monitor_thread = threading.Thread(
        target=monitor_hardware,
        args=(stop_event, samples)
    )

    monitor_thread.start()

    start_time = time.perf_counter()

    try:

        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

    except Exception as error:

        stop_event.set()
        monitor_thread.join()

        print(f"ERROR: {error}")
        continue

    end_time = time.perf_counter()

    stop_event.set()
    monitor_thread.join()

    answer = response["message"]["content"]

    total_time = end_time - start_time

    tokens = response.get("eval_count", 0)

    eval_duration = response.get("eval_duration", 0)

    if eval_duration > 0:

        tokens_per_second = (
            tokens /
            (eval_duration / 1_000_000_000)
        )

    else:

        tokens_per_second = 0


    if samples:

        cpu_values = [
            sample["cpu"]
            for sample in samples
        ]

        ram_values = [
            sample["ram"]
            for sample in samples
        ]

        gpu_values = [
            sample["gpu"]
            for sample in samples
        ]

        vram_values = [
            sample["vram"]
            for sample in samples
        ]

        vram_total = samples[-1]["vram_total"]


        cpu_average = (
            sum(cpu_values) /
            len(cpu_values)
        )

        cpu_peak = max(cpu_values)


        ram_average = (
            sum(ram_values) /
            len(ram_values)
        )

        ram_peak = max(ram_values)


        gpu_average = (
            sum(gpu_values) /
            len(gpu_values)
        )

        gpu_peak = max(gpu_values)


        vram_average = (
            sum(vram_values) /
            len(vram_values)
        )

        vram_peak = max(vram_values)


    else:

        cpu_average = 0
        cpu_peak = 0

        ram_average = 0
        ram_peak = 0

        gpu_average = 0
        gpu_peak = 0

        vram_average = 0
        vram_peak = 0

        vram_total = 0


    vram_average_gb = vram_average / 1024
    vram_peak_gb = vram_peak / 1024
    vram_total_gb = vram_total / 1024


    print(f"Response time: {total_time:.2f}s")
    print(f"Generated tokens: {tokens}")
    print(f"Tokens/sec: {tokens_per_second:.2f}")

    print(f"CPU average: {cpu_average:.1f}%")
    print(f"CPU peak: {cpu_peak:.1f}%")

    print(f"RAM average: {ram_average:.2f} GB")
    print(f"RAM peak: {ram_peak:.2f} GB")

    print(f"GPU average: {gpu_average:.1f}%")
    print(f"GPU peak: {gpu_peak:.1f}%")

    print(f"VRAM average: {vram_average_gb:.2f} GB")
    print(f"VRAM peak: {vram_peak_gb:.2f} GB")
    print(f"VRAM total: {vram_total_gb:.2f} GB")


    with open(
        RESULTS_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            datetime.now().isoformat(),
            MODEL,
            question_id,
            category,
            question,
            answer,
            round(total_time, 4),
            tokens,
            round(tokens_per_second, 2),
            round(cpu_average, 2),
            round(cpu_peak, 2),
            round(ram_average, 2),
            round(ram_peak, 2),
            round(gpu_average, 2),
            round(gpu_peak, 2),
            round(vram_average_gb, 2),
            round(vram_peak_gb, 2),
            round(vram_total_gb, 2)
        ])


print("\n" + "=" * 60)
print("  BENCHMARK COMPLETE")
print(f"Results saved to: {RESULTS_FILE}")
print("=" * 60)