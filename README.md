# Thunderbolt.ai

## Local AI Assistant, RAG and LLM Benchmarking System

Thunderbolt.ai is a local AI assistant and LLM experimentation platform built around Ollama.

The project combines local LLM inference, interactive chat, voice interaction, document-based Retrieval-Augmented Generation (RAG), hardware monitoring, LLM benchmarking, model quality evaluation, performance comparison, and automated reporting.

The main goal is to evaluate local LLMs not only by response quality, but also by latency, generation speed, and hardware resource usage.

---

## Features

### 1. Local LLM Chat

Thunderbolt.ai communicates with locally running language models through Ollama.

The current benchmark includes:

- Qwen2.5-Coder 7B
- Gemma 3 4B
- Qwen3 8B

No cloud LLM API is required for the core local inference pipeline.

---

### 2. Voice Interaction

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
```

This allows the assistant to be used through both text and voice.

---

### 3. Document RAG

Thunderbolt.ai includes document-based Retrieval-Augmented Generation.

PDF documents can be placed inside:

```text
documents/
```

The system processes the document, creates chunks, generates embeddings, retrieves relevant content, and uses the retrieved context when answering document-related questions.

Document mode can be enabled using:

```text
/doc
```

Normal chat mode can be restored using:

```text
/chat
```

---

### 4. Hardware Monitoring

Thunderbolt.ai monitors hardware resources while generating responses.

The system records:

- CPU utilization
- RAM usage
- GPU utilization
- VRAM usage
- Response time
- Generated tokens
- Tokens per second

The collected performance information is stored in CSV files for analysis.

---

### 5. LLM Benchmarking

Thunderbolt.ai contains a benchmarking pipeline for comparing local LLMs.

The benchmark measures:

- Response time
- Generation speed
- Generated tokens
- CPU utilization
- RAM usage
- GPU utilization
- VRAM usage

Benchmark data is stored under:

```text
benchmark/
```

---

### 6. Model Quality Evaluation

Performance is only one part of evaluating a language model.

Thunderbolt.ai also includes a separate quality evaluation pipeline for comparing model responses.

Quality results are stored in:

```text
benchmark/quality_results.csv
```

This allows model quality and hardware performance to be analyzed together.

---

### 7. Model Comparison

The project generates visual comparisons between the tested models.

Current comparison graphs include:

- CPU utilization
- GPU utilization
- RAM usage
- VRAM usage
- Response time
- Tokens per second
- Response quality

Graphs are stored in:

```text
benchmark/graphs/
```

---

### 8. Automated Reporting

Thunderbolt.ai includes scripts for generating benchmark analysis and reports.

The project contains:

- Benchmark analysis
- Model comparison
- Quality evaluation
- Report generation
- PDF report generation

The final benchmark report is available inside:

```text
documents/
```

---

## System Architecture

The overall system can be viewed as:

```text
                    Thunderbolt.ai
                           │
              ┌────────────┴────────────┐
              │                         │
         Chat Interface            Voice Interface
              │                         │
              └────────────┬────────────┘
                           │
                           ▼
                    Local LLM / Ollama
                           │
              ┌────────────┴────────────┐
              │                         │
           Normal Chat             Document RAG
                                        │
                                        ▼
                                   PDF Documents
                                        │
                                        ▼
                                   Embeddings
                                        │
                                        ▼
                                   Retrieval
                                        │
                                        ▼
                                     Context
                           │
                           ▼
                    Generated Response
                           │
              ┌────────────┴────────────┐
              │                         │
        Performance Data          Quality Evaluation
              │                         │
              └────────────┬────────────┘
                           ▼
                  Benchmark Analysis
                           │
                           ▼
                    Graphs + Reports
```

---

## Project Structure

```text
thunderbolt-ai/
│
├── benchmark/
│   ├── graphs/
│   │   ├── cpu_comparison.png
│   │   ├── gpu_comparison.png
│   │   ├── quality_comparison.png
│   │   ├── ram_comparison.png
│   │   ├── response_time_comparison.png
│   │   ├── tokens_per_second_comparison.png
│   │   └── vram_comparison.png
│   │
│   ├── models/
│   │   ├── gemma3-4b.csv
│   │   ├── gemma3-4b-quality.csv
│   │   ├── qwen2.5-coder-7b.csv
│   │   ├── qwen2.5-coder-7b-quality.csv
│   │   ├── qwen3-8b.csv
│   │   └── qwen3-8b-quality.csv
│   │
│   ├── benchmark_results.csv
│   ├── quality_results.csv
│   ├── final_analysis.csv
│   └── questions.json
│
├── documents/
│   └── Thunderbolt_AI_Final_Benchmark_Report.pdf
│
├── benchmark_runner.py
├── compare_models.py
├── evaluate_results.py
├── final_analysis.py
├── generate_report.py
├── generate_pdf_report.py
├── main.py
├── rag.py
├── results.csv
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Bot87Ever/thunderbolt-ai.git
cd thunderbolt-ai
```

### 2. Create a virtual environment

On Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

### 3. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 4. Install Ollama

Thunderbolt.ai uses Ollama for local LLM inference.

Make sure Ollama is installed and running before starting the assistant.

Pull the model required for the assistant, for example:

```powershell
ollama pull qwen2.5-coder:7b
```

Other models can be pulled depending on the benchmark configuration.

---

## Running Thunderbolt.ai

Start the main assistant:

```powershell
python main.py
```

The assistant provides normal chat functionality and additional interaction modes.

Available commands include:

```text
/doc
/chat
/voice
```

### Document Mode

Place a PDF inside:

```text
documents/
```

Then run:

```powershell
python main.py
```

and enable document mode using:

```text
/doc
```

---

## Running the Benchmark

The benchmark pipeline can be started with:

```powershell
python benchmark_runner.py
```

The benchmark generates performance data for the configured models.

Results are stored under:

```text
benchmark/
```

---

## Model Analysis

The project includes separate scripts for analyzing and comparing benchmark results.

### Model Comparison

```powershell
python compare_models.py
```

### Final Analysis

```powershell
python final_analysis.py
```

### Quality Evaluation

```powershell
python evaluate_results.py
```

### Generate Report

```powershell
python generate_report.py
```

### Generate PDF Report

```powershell
python generate_pdf_report.py
```

---

## Benchmark Metrics

Thunderbolt.ai evaluates models using multiple dimensions.

| Category | Metrics |
|---|---|
| Speed | Response time, tokens/second |
| Output | Generated tokens |
| CPU | Average and peak utilization |
| RAM | Average and peak usage |
| GPU | Average and peak utilization |
| VRAM | Average and peak usage |
| Quality | Response quality evaluation |

This allows different models to be compared using both **performance and quality**.

---

## Benchmark Results

The generated benchmark results and graphs are available in:

```text
benchmark/
```

The final benchmark report is available at:

```text
documents/Thunderbolt_AI_Final_Benchmark_Report.pdf
```

The repository also contains model-specific benchmark and quality CSV files.

---

## Design Goal

The goal of Thunderbolt.ai is not simply to run a local LLM.

It is designed as an experimental platform for studying the relationship between:

```text
Model
  ↓
Inference
  ↓
Response Quality
  ↓
Latency
  ↓
Token Generation
  ↓
CPU / RAM / GPU / VRAM Usage
  ↓
Overall Efficiency
```

This provides a practical way to study local LLM performance on consumer hardware.

---

## Technologies Used

- Python
- Ollama
- PyTorch
- Hugging Face
- Sentence Transformers
- scikit-learn
- psutil
- NVIDIA GPU monitoring
- CSV-based data analysis
- Retrieval-Augmented Generation
- Speech recognition
- Text-to-speech

---

## Future Improvements

Possible future improvements include:

- Improved RAG retrieval
- Persistent conversation memory
- Streaming responses
- Improved voice interaction
- More local LLMs for benchmarking
- Larger benchmark datasets
- More automated quality evaluation
- Additional hardware metrics
- Automated model selection based on workload
- Improved retrieval and document processing

---

## Author

**Bot87Ever**

Thunderbolt.ai

Local LLM benchmarking, RAG, voice interaction and AI assistant.