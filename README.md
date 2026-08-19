\# Thunderbolt.ai



\## Local AI Assistant, RAG and LLM Benchmarking System



Thunderbolt.ai is a local AI assistant built around Ollama for running large language models directly on consumer hardware.



The project combines:



\- Local LLM inference

\- Interactive chat

\- Voice input

\- Voice output

\- Document-based RAG

\- Hardware monitoring

\- LLM benchmarking

\- Model quality evaluation

\- Performance comparison

\- Automated benchmark reporting



The system is designed to evaluate how different local LLMs perform in terms of answer quality, latency, generation speed and hardware efficiency.



\---



\## Features



\### 1. Local LLM Chat



Thunderbolt.ai communicates with locally running models through Ollama.



The system can run models such as:



\- Qwen2.5-Coder 7B

\- Gemma 3 4B

\- Qwen3 8B



No cloud LLM API is required for inference.



\---



\### 2. Voice Interaction



Thunderbolt.ai supports voice-based interaction.



The voice pipeline is:



User speech  

→ Speech recognition  

→ Local LLM  

→ Generated response  

→ Text-to-speech



This allows the assistant to be used through both text and voice.



\---



\### 3. Document RAG



Thunderbolt.ai includes document-based Retrieval-Augmented Generation.



PDF documents can be placed inside:



```text

documents/

