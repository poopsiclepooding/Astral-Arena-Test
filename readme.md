# <div align="center">🤖 Astral Arena Test 🪐</div>

<p align="center">
    <a href="https://www.python.org/downloads/release/python-3916/">
        <img alt="Python Version" src="https://img.shields.io/badge/python-3.9+-blue.svg">
    </a>
    <a href="https://github.com/psf/black">
        <img alt="Code Style: Black" src="https://img.shields.io/badge/code%20style-black-black">
    </a>
    <a href="https://huggingface.co/AgentVerse">
        <img alt="HuggingFace" src="https://img.shields.io/badge/hugging_face-play-yellow">
    </a>
    <a href="https://discord.gg/gDAXfjMw">
        <img alt="Discord" src="https://img.shields.io/badge/AgentVerse-Discord-purple?style=flat">
    </a>
</p>

<p align="center">
<img src="./imgs/title.png" width="512">
</p>

<p align="center">
    【<a href="https://arxiv.org/abs/2308.10848">Paper</a>】 
</p>

<p align="center">
    【English | <a href="README_zh.md">Chinese</a>】 
</p>

## What is Astral Arena Test?

Astral Arena Test is a groundbreaking framework designed to pioneer advanced multi-agent systems in virtual environments. Our platform uniquely combines two powerful frameworks: task-solving and simulation, enabling unprecedented opportunities for research and development in artificial intelligence. At its core, Astral Arena Test provides a robust infrastructure for deploying multiple LLM-based agents in various applications, from educational simulations to complex problem-solving scenarios.

## Vision

Our vision extends beyond creating just another multi-agent framework. We aim to:

1. **Revolutionize Multi-Agent Research**: Push the boundaries of what's possible in agent collaboration and emergence studies
2. **Enable Real-World Applications**: Bridge the gap between research prototypes and production-ready multi-agent systems
3. **Foster Innovation**: Provide a platform where researchers and developers can easily experiment with new ideas and approaches
4. **Build Community**: Create an ecosystem where knowledge and resources are shared freely, accelerating the field's progress
5. **Drive Standardization**: Establish best practices and patterns for multi-agent system development


## Why Astral Arena Test?

In the rapidly evolving landscape of artificial intelligence, multi-agent systems represent the next frontier in achieving more sophisticated and nuanced AI behaviors. Astral Arena Test addresses several critical needs in this space:

1. **Unified Framework**: Unlike existing solutions that focus on either simulation or task-solving, Astral Arena Test seamlessly integrates both paradigms into a single, coherent framework.
2. **Scalability**: Our architecture is designed to handle multiple agents with different roles, capabilities, and objectives, making it ideal for complex scenarios and real-world applications.
3. **Flexibility**: The platform supports various LLM backends, from OpenAI's models to local implementations like LLaMA, giving researchers and developers complete control over their agent implementations.
4. **Research-Ready**: Built with academic and industrial research in mind, Astral Arena Test provides comprehensive tools for experimenting with agent behaviors, interactions, and emergent phenomena.
5. **Production-Grade**: While maintaining research flexibility, the framework is robust enough for production deployments, with support for both CLI and GUI interfaces.

# 🚀 Getting Started

## Installation

**Manual Installation (Recommended!)**

**Make sure you have Python >= 3.9**
```bash
git clone https://github.com/OpenBMB/AgentVerse.git --depth 1
cd AgentVerse
pip install -e .
```

For local model support (LLaMA, etc.):
```bash
pip install -r requirements_local.txt
```

**Install with pip**
```bash
pip install -U agentverse
```

## Environment Variables
```bash
# Export your OpenAI API key
export OPENAI_API_KEY="your_api_key_here"

# For Azure OpenAI services:
export AZURE_OPENAI_API_KEY="your_api_key_here"
export AZURE_OPENAI_API_BASE="your_api_base_here"
```

## Simulation

### Framework Required Modules 
```
- agentverse 
  - agents
    - simulation_agent
  - environments
    - simulation_env
```

### CLI Example
```shell
agentverse-simulation --task simulation/nlp_classroom_9players
```

### GUI Example
```shell
agentverse-simulation-gui --task simulation/nlp_classroom_9players
```
Visit [http://127.0.0.1:7860/](http://127.0.0.1:7860/) after launching.

For simulation cases with tools:
```bash
git clone git+https://github.com/OpenBMB/BMTools.git
cd BMTools
pip install -r requirements.txt
python setup.py develop
```

## Task-Solving 

### Framework Required Modules 
```
- agentverse 
  - agents
    - simulation_env
  - environments
    - tasksolving_env
```

### CLI Example

For benchmark testing:
```shell
agentverse-benchmark --task tasksolving/humaneval/gpt-3.5 --dataset_path data/humaneval/test.jsonl --overwrite
```

For single queries:
```shell
agentverse-tasksolving --task tasksolving/brainstorming
```

## Local Model Support

### vLLM Support
1. Install and setup vLLM server
2. Set environment variables:
```bash
export VLLM_API_KEY="your_api_key_here"
export VLLM_API_BASE="http://your_vllm_url_here"
```
3. Modify config:
```yaml
model_type: vllm
model: llama-2-7b-chat-hf
```

### FSChat Support
1. Install dependencies:
```bash
pip install -r requirements_local.txt
```

2. Launch local server:
```bash
bash scripts/run_local_model_server.sh
```

3. Modify config:
```yaml
llm:
  llm_type: local
  model: llama-2-7b-chat-hf
```

