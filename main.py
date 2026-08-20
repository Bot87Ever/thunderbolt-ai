import os
import time
import threading
import warnings

import ollama
import psutil
import speech_recognition as sr
import pyttsx3
from colorama import init, Fore

from rag import load_documents, ask_document

warnings.filterwarnings("ignore")

init(autoreset=True)

MODEL = "gemma3:4b"

conversation_history = []

recognizer = sr.Recognizer()
recognizer.pause_threshold = 2.5
recognizer.non_speaking_duration = 1.0
recognizer.phrase_threshold = 0.3

speaker = pyttsx3.init()


def get_gpu_stats():
    try:
        import pynvml

        pynvml.nvmlInit()

        handle = pynvml.nvmlDeviceGetHandleByIndex(0)

        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
        memory = pynvml.nvmlDeviceGetMemoryInfo(handle)

        gpu_percent = util.gpu
        vram_used = memory.used / (1024 ** 3)
        vram_total = memory.total / (1024 ** 3)

        pynvml.nvmlShutdown()

        return gpu_percent, vram_used, vram_total

    except Exception:
        return 0.0, 0.0, 0.0


def monitor_hardware(stop_event, stats):
    cpu_values = []
    ram_values = []
    gpu_values = []
    vram_values = []
    vram_total = 0.0

    while not stop_event.is_set():

        cpu = psutil.cpu_percent(interval=0.5)

        ram = psutil.virtual_memory().used / (1024 ** 3)

        gpu, vram, vram_total = get_gpu_stats()

        cpu_values.append(cpu)
        ram_values.append(ram)
        gpu_values.append(gpu)
        vram_values.append(vram)

        time.sleep(0.5)

    if cpu_values:
        stats["cpu_avg"] = sum(cpu_values) / len(cpu_values)
        stats["cpu_peak"] = max(cpu_values)

    if ram_values:
        stats["ram_avg"] = sum(ram_values) / len(ram_values)
        stats["ram_peak"] = max(ram_values)

    if gpu_values:
        stats["gpu_avg"] = sum(gpu_values) / len(gpu_values)
        stats["gpu_peak"] = max(gpu_values)

    if vram_values:
        stats["vram_avg"] = sum(vram_values) / len(vram_values)
        stats["vram_peak"] = max(vram_values)

    stats["vram_total"] = vram_total


def speak(text):
    try:
        speaker.say(text)
        speaker.runAndWait()

    except Exception:
        pass


def listen():

    with sr.Microphone() as source:

        print(
            Fore.YELLOW +
            "\nListening..."
        )

        recognizer.adjust_for_ambient_noise(
            source,
            duration=1
        )

        try:

            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=60
            )

        except sr.WaitTimeoutError:

            print(
                Fore.RED +
                "No speech detected."
            )

            return ""

    try:

        print(
            Fore.YELLOW +
            "Recognizing..."
        )

        text = recognizer.recognize_google(
            audio
        )

        print(
            Fore.CYAN +
            "You [voice]: " +
            text
        )

        return text

    except sr.UnknownValueError:

        print(
            Fore.RED +
            "Could not understand the audio."
        )

        return ""

    except sr.RequestError:

        print(
            Fore.RED +
            "Speech recognition service unavailable."
        )

        return ""


def normal_chat(prompt):

    global conversation_history

    conversation_history.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    stop_event = threading.Event()

    stats = {}

    monitor_thread = threading.Thread(
        target=monitor_hardware,
        args=(stop_event, stats)
    )

    monitor_thread.start()

    start_time = time.time()

    print(
        Fore.GREEN +
        "\nThunderbolt.ai:"
    )

    answer = ""

    try:

        stream = ollama.chat(
            model=MODEL,
            messages=conversation_history,
            stream=True
        )

        for chunk in stream:

            content = chunk[
                "message"
            ][
                "content"
            ]

            answer += content

            print(
                content,
                end="",
                flush=True
            )

    except Exception as e:

        print(
            Fore.RED +
            f"\nError: {e}"
        )

        conversation_history.pop()

        stop_event.set()

        monitor_thread.join()

        return ""

    print()

    end_time = time.time()

    stop_event.set()

    monitor_thread.join()

    conversation_history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    response_time = (
        end_time -
        start_time
    )

    generated_tokens = len(
        answer.split()
    )

    tokens_per_second = (
        generated_tokens /
        response_time
        if response_time > 0
        else 0
    )

    print(
        Fore.WHITE +
        "\n──────── PERFORMANCE ────────"
    )

    print(
        "Mode: CHAT"
    )

    print(
        f"Response time: "
        f"{response_time:.2f} seconds"
    )

    print(
        f"Generated tokens: "
        f"{generated_tokens}"
    )

    print(
        f"Tokens/second: "
        f"{tokens_per_second:.2f}"
    )

    print(
        f"CPU average: "
        f"{stats.get('cpu_avg', 0):.1f}%"
    )

    print(
        f"CPU peak: "
        f"{stats.get('cpu_peak', 0):.1f}%"
    )

    print(
        f"RAM average: "
        f"{stats.get('ram_avg', 0):.2f} GB"
    )

    print(
        f"RAM peak: "
        f"{stats.get('ram_peak', 0):.2f} GB"
    )

    print(
        f"GPU average: "
        f"{stats.get('gpu_avg', 0):.1f}%"
    )

    print(
        f"GPU peak: "
        f"{stats.get('gpu_peak', 0):.1f}%"
    )

    print(
        f"VRAM average: "
        f"{stats.get('vram_avg', 0):.2f} GB"
    )

    print(
        f"VRAM peak: "
        f"{stats.get('vram_peak', 0):.2f} GB"
    )

    print(
        f"VRAM total: "
        f"{stats.get('vram_total', 0):.2f} GB"
    )

    print(
        "─────────────────────────────"
    )

    return answer


def document_chat(prompt):

    stop_event = threading.Event()

    stats = {}

    monitor_thread = threading.Thread(
        target=monitor_hardware,
        args=(stop_event, stats)
    )

    monitor_thread.start()

    start_time = time.time()

    print(
        Fore.GREEN +
        "\nThunderbolt.ai [RAG]:"
    )

    answer = ""

    try:

        result = ask_document(
            prompt
        )

        if isinstance(
            result,
            str
        ):

            answer = result

        elif isinstance(
            result,
            dict
        ):

            answer = result.get(
                "answer",
                ""
            )

        else:

            answer = str(result)

        print(answer)

    except Exception as e:

        print(
            Fore.RED +
            f"\nRAG Error: {e}"
        )

    end_time = time.time()

    stop_event.set()

    monitor_thread.join()

    response_time = (
        end_time -
        start_time
    )

    generated_tokens = len(
        answer.split()
    )

    tokens_per_second = (
        generated_tokens /
        response_time
        if response_time > 0
        else 0
    )

    print(
        Fore.WHITE +
        "\n──────── PERFORMANCE ────────"
    )

    print(
        "Mode: RAG"
    )

    print(
        f"Response time: "
        f"{response_time:.2f} seconds"
    )

    print(
        f"Generated tokens: "
        f"{generated_tokens}"
    )

    print(
        f"Tokens/second: "
        f"{tokens_per_second:.2f}"
    )

    print(
        f"CPU average: "
        f"{stats.get('cpu_avg', 0):.1f}%"
    )

    print(
        f"CPU peak: "
        f"{stats.get('cpu_peak', 0):.1f}%"
    )

    print(
        f"RAM average: "
        f"{stats.get('ram_avg', 0):.2f} GB"
    )

    print(
        f"RAM peak: "
        f"{stats.get('ram_peak', 0):.2f} GB"
    )

    print(
        f"GPU average: "
        f"{stats.get('gpu_avg', 0):.1f}%"
    )

    print(
        f"GPU peak: "
        f"{stats.get('gpu_peak', 0):.1f}%"
    )

    print(
        f"VRAM average: "
        f"{stats.get('vram_avg', 0):.2f} GB"
    )

    print(
        f"VRAM peak: "
        f"{stats.get('vram_peak', 0):.2f} GB"
    )

    print(
        f"VRAM total: "
        f"{stats.get('vram_total', 0):.2f} GB"
    )

    print(
        "─────────────────────────────"
    )

    return answer


def voice_chat():

    prompt = listen()

    if not prompt:
        return

    answer = normal_chat(
        prompt
    )

    if answer:

        print(
            Fore.YELLOW +
            "\nSpeaking..."
        )

        speak(answer)


def clear_memory():

    global conversation_history

    conversation_history.clear()

    print(
        Fore.YELLOW +
        "\nConversation memory cleared."
    )


def main():

    print(
        "\nLoading Thunderbolt.ai..."
    )

    try:

        load_documents()

        print(
            "Reading document: "
            "Thunderbolt_AI_Final_Benchmark_Report.pdf"
        )

    except Exception as e:

        print(
            Fore.YELLOW +
            f"Document loading warning: {e}"
        )

    print(
        "\n" +
        "=" * 60
    )

    print(
        "                 THUNDERBOLT.AI"
    )

    print(
        "=" * 60
    )

    print(
        f"Model: {MODEL}"
    )

    print(
        "Document knowledge: READY (9 chunks)"
    )

    print("\nCommands:")

    print(
        "  /doc    Ask using uploaded documents"
    )

    print(
        "  /chat   Normal AI conversation"
    )

    print(
        "  /voice  Ask using your microphone"
    )

    print(
        "  /clear  Clear conversation memory"
    )

    print(
        "  exit    Quit"
    )

    mode = "chat"

    while True:

        try:

            prompt = input(
                f"\nYou [{mode}]: "
            ).strip()

        except KeyboardInterrupt:

            print("\n")

            break

        except EOFError:

            print("\n")

            break

        if not prompt:

            continue

        if prompt.lower() == "exit":

            break

        if prompt.lower() == "/clear":

            clear_memory()

            continue

        if prompt.lower() == "/chat":

            mode = "chat"

            print(
                "Switched to normal chat mode."
            )

            continue

        if prompt.lower() == "/doc":

            mode = "doc"

            print(
                "Switched to document mode."
            )

            continue

        if prompt.lower() == "/voice":

            voice_chat()

            continue

        if mode == "doc":

            document_chat(
                prompt
            )

        else:

            normal_chat(
                prompt
            )


if __name__ == "__main__":

    main()
