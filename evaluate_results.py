import csv
import os

INPUT_FILE = "benchmark/benchmark_results.csv"
OUTPUT_FILE = "benchmark/quality_results.csv"


EXPECTED_CONCEPTS = {
    1: [
        "second largest",
        "array",
        "o(n)",
        "o(1)"
    ],

    2: [
        "binary search",
        "sorted",
        "o(log n)",
        "middle"
    ],

    3: [
        "division by zero",
        "zero",
        "undefined"
    ],

    4: [
        "maximum",
        "initial",
        "arr[0]",
        "max"
    ],

    5: [
        "stack",
        "queue",
        "lifo",
        "fifo"
    ],

    6: [
        "merge sort",
        "o(n log n)",
        "divide",
        "merge"
    ],

    7: [
        "bfs",
        "dfs",
        "queue",
        "stack"
    ],

    8: [
        "process",
        "thread",
        "memory",
        "shared"
    ],

    9: [
        "1nf",
        "2nf",
        "3nf",
        "normalization"
    ],

    10: [
        "syn",
        "ack",
        "three-way",
        "handshake"
    ]
}


def calculate_score(question_id, answer):

    answer_lower = answer.lower()

    concepts = EXPECTED_CONCEPTS.get(question_id, [])

    if not concepts:
        return 0, 0, []


    matched = []

    for concept in concepts:

        if concept.lower() in answer_lower:
            matched.append(concept)


    score = (len(matched) / len(concepts)) * 10

    return round(score, 2), len(matched), matched


if not os.path.exists(INPUT_FILE):

    print("ERROR:")
    print(f"File not found: {INPUT_FILE}")
    print("Run benchmark_runner.py first.")

    exit()


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    rows = list(reader)


with open(
    OUTPUT_FILE,
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
        "quality_score",
        "matched_concepts",
        "total_concepts",
        "response_time",
        "tokens_per_second",
        "gpu_peak",
        "vram_peak_gb"
    ])


total_score = 0


for row in rows:

    question_id = int(row["question_id"])

    answer = row["answer"]

    score, matched_count, matched = calculate_score(
        question_id,
        answer
    )

    total_score += score

    print(
        f"[{question_id}] "
        f"{row['category']} "
        f"→ Score: {score}/10"
    )

    print(
        f"   Matched: {matched_count}/"
        f"{len(EXPECTED_CONCEPTS[question_id])}"
    )

    with open(
        OUTPUT_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as output_file:

        writer = csv.writer(output_file)

        writer.writerow([
            row["timestamp"],
            row["model"],
            row["question_id"],
            row["category"],
            row["question"],
            score,
            matched_count,
            len(EXPECTED_CONCEPTS[question_id]),
            row["response_time"],
            row["tokens_per_second"],
            row["gpu_peak"],
            row["vram_peak_gb"]
        ])


if rows:

    average_score = total_score / len(rows)

else:

    average_score = 0


print("\n" + "=" * 50)
print("⚡ THUNDERBOLT.AI QUALITY EVALUATION")
print("=" * 50)

print(f"Model: {rows[0]['model']}")
print(f"Questions evaluated: {len(rows)}")
print(f"Average quality score: {average_score:.2f}/10")

print("=" * 50)

print(
    f"Results saved to: {OUTPUT_FILE}"
)