import time
import csv
import os
import subprocess
import psutil
from datetime import datetime
import ollama
import threading
import faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import speech_recognition as sr
import pyttsx3


MODEL = "gemma3:4b"
RESULTS_FILE = "results.csv"

DOCUMENT_FOLDER = "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 4


# ============================================================
# GPU MONITORING
# ============================================================

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


# ============================================================
# RAG
# ============================================================

def read_pdf(path):

    reader = PdfReader(path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def split_text(text):

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def load_documents():

    chunks = []

    if not os.path.exists(DOCUMENT_FOLDER):
        os.makedirs(DOCUMENT_FOLDER)

    for filename in os.listdir(DOCUMENT_FOLDER):

        if filename.lower().endswith(".pdf"):

            path = os.path.join(
                DOCUMENT_FOLDER,
                filename
            )

            print(f"Reading document: {filename}")

            text = read_pdf(path)

            document_chunks = split_text(text)

            chunks.extend(document_chunks)

    return chunks


def create_vector_index(chunks, embedder):

    if not chunks:
        return None

    embeddings = embedder.encode(
        chunks,
        convert_to_numpy=True
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


def retrieve_document_context(
    question,
    chunks,
    index,
    embedder
):

    if index is None or not chunks:
        return ""

    question_embedding = embedder.encode(
        [question],
        convert_to_numpy=True
    )

    distances, indices = index.search(
        question_embedding,
        min(TOP_K, len(chunks))
    )

    relevant_chunks = []

    for i in indices[0]:

        if 0 <= i < len(chunks):

            relevant_chunks.append(
                chunks[i]
            )

    return "\n\n---\n\n".join(
        relevant_chunks
    )


# ============================================================
# VOICE
# ============================================================

recognizer = sr.Recognizer()

recognizer.pause_threshold = 2.0
recognizer.non_speaking_duration = 0.8
recognizer.phrase_threshold = 0.3

speaker = pyttsx3.init()


def listen():

    try:

        with sr.Microphone() as source:

            print()
            print("🎙️ Listening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=60
            )

        try:

            text = recognizer.recognize_google(
                audio
            )

            print(
                f"You said: {text}"
            )

            return text

        except sr.UnknownValueError:

            print(
                "Could not understand the audio."
            )

            return ""

        except sr.RequestError:

            print(
                "Speech recognition service unavailable."
            )

            return ""

    except sr.WaitTimeoutError:

        print(
            "Listening timed out."
        )

        return ""

    except Exception as e:

        print(
            f"Microphone error: {e}"
        )

        return ""


def speak(text):

    try:

        speaker.say(text)

        speaker.runAndWait()

    except Exception as e:

        print(
            f"Voice output error: {e}"
        )


# ============================================================
# CSV
# ============================================================

if not os.path.exists(RESULTS_FILE):

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
            "question",
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


# ============================================================
# LOAD RAG
# ============================================================

print()
print("Loading Thunderbolt.ai...")

embedder = SentenceTransformer(
    EMBEDDING_MODEL
)

document_chunks = load_documents()

vector_index = create_vector_index(
    document_chunks,
    embedder
)


# ============================================================
# START
# ============================================================

print()
print("=" * 60)
print("                 THUNDERBOLT.AI")
print("=" * 60)

print(f"Model: {MODEL}")

if document_chunks:

    print(
        f"Document knowledge: READY "
        f"({len(document_chunks)} chunks)"
    )

else:

    print(
        "Document knowledge: No PDFs loaded"
    )

print()

print("Commands:")
print("  /doc    Ask using uploaded documents")
print("  /chat   Normal AI conversation")
print("  /voice  Ask using your microphone")
print("  exit    Quit")

print()


mode = "chat"


# ============================================================
# CHAT LOOP
# ============================================================

while True:

    question = input(
        f"You [{mode}]: "
    ).strip()


    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if question.lower() == "exit":

        break


    # --------------------------------------------------------
    # DOCUMENT MODE
    # --------------------------------------------------------

    if question.lower() == "/doc":

        if not document_chunks:

            print()
            print("Thunderbolt.ai:")
            print(
                "No PDF documents are loaded."
            )
            print()

            continue

        mode = "doc"

        print()
        print(
            "Document mode enabled."
        )
        print()

        continue


    # --------------------------------------------------------
    # CHAT MODE
    # --------------------------------------------------------

    if question.lower() == "/chat":

        mode = "chat"

        print()
        print(
            "Normal chat mode enabled."
        )
        print()

        continue


    # --------------------------------------------------------
    # VOICE MODE
    # --------------------------------------------------------

    if question.lower() == "/voice":

        question = listen()

        if not question:

            continue


    # --------------------------------------------------------
    # EMPTY INPUT
    # --------------------------------------------------------

    if not question:

        continue


    # --------------------------------------------------------
    # HARDWARE MONITORING START
    # --------------------------------------------------------

    samples = []

    stop_event = threading.Event()

    monitor_thread = threading.Thread(
        target=monitor_hardware,
        args=(
            stop_event,
            samples
        )
    )

    monitor_thread.start()

    start_time = time.perf_counter()


    # --------------------------------------------------------
    # BUILD PROMPT
    # --------------------------------------------------------

    if mode == "doc":

        context = retrieve_document_context(
            question,
            document_chunks,
            vector_index,
            embedder
        )

        prompt = f"""
You are Thunderbolt.ai.

You are currently answering questions using
the user's documents.

Use ONLY the document context below when answering.

If the answer cannot be found in the document
context, say:

"I could not find that information in the document."

Do not invent information.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

    else:

        prompt = question


    # --------------------------------------------------------
    # OLLAMA - STREAMING
    # --------------------------------------------------------

    answer = ""

    stream_start_time = time.perf_counter()

    try:

        print()
        print("Thunderbolt.ai:")

        stream = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True
        )

        for chunk in stream:

            content = chunk["message"]["content"]

            answer += content

            print(
                content,
                end="",
                flush=True
            )

        print()

    except Exception as e:

        print()
        print(
            f"Thunderbolt.ai error: {e}"
        )
        print()

        stop_event.set()

        monitor_thread.join()

        continue

    finally:

        end_time = time.perf_counter()

        stop_event.set()

        monitor_thread.join()


    # --------------------------------------------------------
    # RESPONSE METRICS
    # --------------------------------------------------------

    total_time = (
        end_time -
        start_time
    )

    # Approximate generated token count
    # using whitespace-separated words.
    tokens = len(answer.split())

    if total_time > 0:

        tokens_per_second = (
            tokens /
            total_time
        )

    else:

        tokens_per_second = 0


    # --------------------------------------------------------
    # HARDWARE METRICS
    # --------------------------------------------------------

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

        cpu_peak = max(
            cpu_values
        )


        ram_average = (
            sum(ram_values) /
            len(ram_values)
        )

        ram_peak = max(
            ram_values
        )


        gpu_average = (
            sum(gpu_values) /
            len(gpu_values)
        )

        gpu_peak = max(
            gpu_values
        )


        vram_average = (
            sum(vram_values) /
            len(vram_values)
        )

        vram_peak = max(
            vram_values
        )

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


    vram_average_gb = (
        vram_average /
        1024
    )

    vram_peak_gb = (
        vram_peak /
        1024
    )

    vram_total_gb = (
        vram_total /
        1024
    )


    # --------------------------------------------------------
    # PERFORMANCE OUTPUT
    # --------------------------------------------------------

    print()

    print(
        "──────── PERFORMANCE ────────"
    )

    print(
        f"Mode: {mode.upper()}"
    )

    print(
        f"Response time: "
        f"{total_time:.2f} seconds"
    )

    print(
        f"Generated tokens: "
        f"{tokens}"
    )

    print(
        f"Tokens/second: "
        f"{tokens_per_second:.2f}"
    )

    print(
        f"CPU average: "
        f"{cpu_average:.1f}%"
    )

    print(
        f"CPU peak: "
        f"{cpu_peak:.1f}%"
    )

    print(
        f"RAM average: "
        f"{ram_average:.2f} GB"
    )

    print(
        f"RAM peak: "
        f"{ram_peak:.2f} GB"
    )

    print(
        f"GPU average: "
        f"{gpu_average:.1f}%"
    )

    print(
        f"GPU peak: "
        f"{gpu_peak:.1f}%"
    )

    print(
        f"VRAM average: "
        f"{vram_average_gb:.2f} GB"
    )

    print(
        f"VRAM peak: "
        f"{vram_peak_gb:.2f} GB"
    )

    print(
        f"VRAM total: "
        f"{vram_total_gb:.2f} GB"
    )

    print(
        "─────────────────────────────"
    )

    print()


    # --------------------------------------------------------
    # VOICE OUTPUT
    # --------------------------------------------------------

    speak(answer)


    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

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
            question,
            round(
                total_time,
                4
            ),
            tokens,
            round(
                tokens_per_second,
                2
            ),
            round(
                cpu_average,
                2
            ),
            round(
                cpu_peak,
                2
            ),
            round(
                ram_average,
                2
            ),
            round(
                ram_peak,
                2
            ),
            round(
                gpu_average,
                2
            ),
            round(
                gpu_peak,
                2
            ),
            round(
                vram_average_gb,
                2
            ),
            round(
                vram_peak_gb,
                2
            ),
            round(
                vram_total_gb,
                2
            )
        ])