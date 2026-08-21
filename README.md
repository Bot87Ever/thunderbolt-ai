# Thunderbolt.ai

## Local AI Assistant, RAG and LLM Benchmarking System

Thunderbolt.ai is a local AI assistant and LLM experimentation platform built around **Ollama**.

The project combines:

- Local LLM inference
- Interactive text chat
- Voice interaction
- Document-based Retrieval-Augmented Generation (RAG)
- Conversation memory
- CPU, RAM, GPU and VRAM monitoring
- LLM benchmarking
- Model quality evaluation
- Model performance comparison
- Automated analysis
- CSV-based result storage
- Graph generation
- PDF report generation

The main goal of Thunderbolt.ai is to evaluate local LLMs not only by their response quality, but also by their **latency, generation speed, token generation and hardware resource usage**.

---

# Features

## 1. Local LLM Chat

Thunderbolt.ai communicates with locally running language models through Ollama.

The current benchmark includes:

- Qwen2.5-Coder 7B
- Gemma 3 4B
- Qwen3 8B

No cloud LLM API is required for the core local inference pipeline.

The assistant supports normal conversational interaction and maintains conversation history during the session.

---

## 2. Voice Interaction

Thunderbolt.ai supports voice-based interaction.

The voice pipeline follows:

```text
User Speech
     ↓
Speech Recognition
     ↓
Local LLM
     ↓
Generated Response
     ↓
Text-to-Speech