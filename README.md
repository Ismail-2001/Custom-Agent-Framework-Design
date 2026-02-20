<div align="center">

# 🌌 Nexus: Custom Agent Framework
### A High-Performance Architectural Blueprint for Production-Grade Autonomous Agents

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![DeepSeek V3](https://img.shields.io/badge/DeepSeek_V3-Orchestrator-6366F1?style=for-the-badge)](https://deepseek.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-Persistence-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-Type_Safety-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](./LICENSE)

<br/>

> *"Designed from first principles to solve the gap between chat scripts and autonomous system reasoning."*

**Nexus (Custom Agent Framework)** is a modular, production-ready framework for building high-autonomy AI agents. It moves beyond simple prompt-wrapping to provide a robust **Self-Correction (Reflective) ReAct loop**, multi-layered persistent memory, and a type-safe state machine for deterministic agentic behavior.

[**🔬 Engineering Logic**](#-engineering-logic) · [**🏗️ Architecture**](#-system-architecture) · [**🚀 Quick Start**](#-quick-start) · [**🧪 Lab & Roadmap**](#-the-lab--roadmap)

---

</div>

## 📌 The Engineering Problem

Most AI agent implementations suffer from three critical "Brittleness Factors":

1.  **Memory Drift**: Agents lose context over long tasks or hallucinate their own state history.
2.  **Logic Lock**: When an LLM makes a mistake, the agent continues down the wrong path indefinitely.
3.  **State Opacity**: It's often impossible to reconstruct *why* an agent made a specific tool choice.

**Nexus solves these** by externalizing the agent's internal state into a Pydantic-guarded machine, implementing a persistent SQLite memory layer, and introducing a **Reflector Node** that critiques the agent's progress every N iterations.

---

## 🔬 Engineering Logic

### 🔄 The Reflective ReAct Cycle
Nexus implements an enhanced **Reasoning + Acting (ReAct)** loop. Unlike standard loops, Nexus includes:
- **Dynamic Scratchpad**: A strictly managed text area where the agent's internal monologue and tool observations are curated.
- **Autonomous Reflector**: A background node that critiques the current execution trace and suggests "Adaptive Replanning" if the agent stalls.
- **Constraint Parsing**: A regex-based structured parser that forces the LLM to adhere to the `Thought → Action → Observation` sequence.

### 🧠 Multi-Layered Memory Hierarchy
Memory in Nexus is not just a chat history; it's a tiered architecture:
- **Short-Term (Conversation)**: Sliding-window token-aware buffer for active context.
- **Long-Term (Fact Storage)**: Persistent SQLite-backed key-value store for cross-session knowledge.
- **Episodic (Experience)**: Complete session "Experience Replays" stored as traces, allowing the agent to "recall" past multi-step successes.
- **Vector (Semantic - Placeholder)**: Structural support for ChromaDB/Pinecone semantic retrieval integration.

### 🛡️ State Sovereignty & Checkpointing
The `StateManager` treats every task as a stateful session:
- **Pydantic Guarding**: The `AgentState` ensures all history and status transitions are type-safe.
- **Atomic Checkpoints**: Save the entire agent universe (memory, history, iteration count) to disk mid-task.
- **Crash Recovery**: Restore an agent from a `checkpoint_id` to resume execution exactly where it left off.

---

## 🏗️ System Architecture

### Internal Orchestration Map

```text
┌──────────────────────────────────────────────────────────────────┐
│                          Core Interface                          │
│        ┌───────────────┐        ┌───────────────┐                │
│        │ Agent (Entry) │        │ State Manager │                │
│        └───────┬───────┘        └───────┬───────┘                │
└────────────────┼────────────────────────┼────────────────────────┘
                 ▼                        │
┌─────────────────────────────────────────┼────────────────────────┐
│                    Agent Executor       ▼                        │
│  ┌──────────────┐    ┌─────────────┐    ┌──────────────┐         │
│  │   Planner    │───▶│   Loop      │◀──▶│  Persistence │         │
│  └──────────────┘    │ (ReAct)     │    └──────────────┘         │
│           ▲          └──────┬──────┘                             │
│           │                 │                                    │
│           │                 ▼                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐        │
│  │   Parser     │◀───│   Reflector  │    │ Tool Manager │        │
│  └──────────────┘    └──────────────┘    └──────┬───────┘        │
└─────────────────────────────────────────────────┼────────────────┘
                                                  ▼
┌───────────────────────────┐         ┌────────────────────────────┐
│      Memory Manager       │         │       LLM Providers        │
│ ┌─────────┐   ┌─────────┐ │         │ ┌─────────┐    ┌─────────┐ │
│ │ Short   │   │ Long    │ │         │ │ OpenAI  │    │ Anthropic│ │
│ └─────────┘   └─────────┘ │         │ └─────────┘    └─────────┘ │
│ ┌─────────┐   ┌─────────┐ │         └────────────────────────────┘
│ │ Episodic│   │ Vector  │ │
│ └─────────┘   └─────────┘ │
└───────────────────────────┘
```

### Module Breakdown

| Namespace | Responsibility |
|---|---|
| `core/executor` | The heart of the machine. Manages the iteration limit and state transitions. |
| `core/reflector` | Intelligence guardian. Critiques the execution trace every 3-5 steps. |
| `memory/episodic` | Records "Experience Traces" — allows agents to learn from past trajectories. |
| `state/persistence` | Handles the physical serialization of state to SQLite or files. |
| `tools/executor` | Safe sub-process/function execution with 0-risk validation. |
| `observability/logger` | Structured JSON logging for integration with Datadog/ELK. |

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/Ismail-2001/Custom-Agent-Framework-Design.git
cd Custom-Agent-Framework-Design
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Open .env and add your keys:
# DEEPSEEK_API_KEY=sk-...
# OPENAI_API_KEY=sk-...
```

### 3. Initialize the Agent

```python
import asyncio
from core.agent import Agent
from llm.openai_provider import OpenAIProvider
from memory.manager import MemoryManager

async def run_lab():
    # 1. Setup Intelligence
    llm = OpenAIProvider(model="gpt-4o")
    memory = MemoryManager()
    
    # 2. Instantiate Agent
    agent = Agent(llm=llm, memory=memory)
    
    # 3. Execute with Persistence
    result = await agent.run(
        "Generate a report on AI trends and save the checkpoint.",
        pattern="react",
        use_planning=True
    )
    
    # 4. Access Trace
    print(f"Final Outcome: {result['output']}")
    print(f"History Size: {len(result['state']['history'])}")

asyncio.run(run_lab())
```

---

## 🧪 The Lab & Roadmap

### ✅ Phase 1-6: Core Framework & Cognitive Depth (Completed)
- [x] **State Machine Core**: Deterministic status management (Pending → Running → Completed).
- [x] **Episodic Replay**: SQLite storage of full task sequences.
- [x] **Self-Reflection Loop**: Autonomous critique node that monitors execution quality.
- [x] **Adaptive Replanning**: Logic to adjust strategy when progress stalls.
- [x] **Tool Guardrail System**: JSON Schema validation for all agent actions.
- [x] **Structured Trace Logger**: Time-stamped, categorized event logging.

### 🔨 Phase 7: Scaling & Integrations (Next)
- [ ] **Multi-Agent Handover**: Logic for one agent to delegate to another.
- [ ] **Adaptive Rate Limiting**: Intelligent backoff logic for LLM APIs.
- [ ] **Graph-Based Planning**: Moving from a linear list to a task dependency graph.
- [ ] **OTEL Integration**: Full OpenTelemetry support for cloud-native tracing.
- [ ] **Distributed Memory**: Redis-backed memory for cluster deployments.
- [ ] **Human-in-the-loop (HITL)**: Tool calls that wait for human approval via state suspension.

---

## 🧪 Testing Protocol

Nexus includes a high-coverage test suite built for framework integrity:

```bash
# Run Core System Tests
pytest tests/test_core.py

# Run Memory Persistence Tests
pytest tests/test_memory.py

# Run State Recovery Integration Tests
pytest tests/test_state.py
```

---

<div align="center">

**Built for systems engineers. Perfected for AI autonomy.**

*If this framework helped you understand agent architecture, star ⭐ the repo.*

Built with ❤️ by [Ismail Sajid](https://github.com/Ismail-2001)

</div>
