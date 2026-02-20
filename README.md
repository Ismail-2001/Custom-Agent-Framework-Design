# Custom Agent Framework

A production-grade agentic AI framework built from first principles, demonstrating deep understanding of agent architecture, tool integration, memory systems, and state management.

## 🎯 Project Overview

This framework implements core agent concepts including:
- **ReAct Pattern**: Reason and Act in iterative loops
- **Multi-layered Memory**: Short-term, long-term, episodic, and vector storage
- **State Management**: Persistence, checkpointing, and recovery
- **Tool System**: Dynamic tool discovery and safe execution
- **Observability**: Comprehensive logging and metrics

## 🏗️ Architecture

```
CustomAgentFramework/
├── core/
│   ├── agent.py              # Main agent orchestrator
│   ├── executor.py           # Agent loop execution (ReAct)
│   ├── planner.py            # Task planning and decomposition
│   └── decision_maker.py     # Action selection logic
├── memory/
│   ├── base.py              # Abstract memory interface
│   ├── short_term.py        # Conversation/working memory
│   ├── long_term.py         # Persistent storage (SQLite)
│   ├── episodic.py          # Experience replay
│   ├── vector_store.py      # Semantic memory (placeholder)
│   └── manager.py           # Memory orchestration
├── tools/
│   ├── base.py              # Tool abstraction
│   └── executor.py          # Safe tool execution
├── state/
│   ├── manager.py           # State orchestration
│   ├── persistence.py       # Checkpoint and recovery
│   ├── serialization.py     # State serialization
│   └── versioning.py        # State version control
├── llm/
│   ├── provider.py          # LLM abstraction layer
│   ├── openai_provider.py   # OpenAI implementation
│   ├── prompt_builder.py    # Dynamic prompt construction
│   └── parser.py            # Response parsing (ReAct format)
└── observability/
    ├── logger.py            # Structured logging
    └── metrics.py           # Performance metrics
```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### Basic Usage

```python
import asyncio
from llm.openai_provider import OpenAIProvider
from core.agent import Agent
from tools.base import Tool

# Define a custom tool
class CalculatorTool(Tool):
    name = "calculator"
    description = "Perform arithmetic operations"
    parameters = {
        "type": "object",
        "properties": {
            "operation": {"type": "string"},
            "a": {"type": "number"},
            "b": {"type": "number"}
        }
    }
    
    async def _run(self, operation, a, b):
        if operation == "add":
            return a + b
        # ... other operations

# Create agent
llm = OpenAIProvider(model="gpt-4o-mini")
tools = [CalculatorTool()]
agent = Agent(llm=llm, tools=tools)

# Run a task
result = await agent.run("What is 15 times 7, then add 10?", pattern="react")
print(result["output"])
```

### Running Demos

```bash
# Basic demo (uses mock LLM if no API key)
python demo.py

# Advanced demo (memory, checkpoints, metrics)
python demo_advanced.py
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_core.py
```

## 📚 Core Features

### 1. **ReAct Agent Loop**

The framework implements the ReAct (Reasoning and Acting) pattern:

```
Observe → Think → Act → Observe → ...
```

Agents reason about tasks, select appropriate tools, execute actions, and learn from observations.

### 2. **Memory System**

**Short-Term Memory**: Conversation buffer with sliding window
- Maintains recent conversation history
- Automatic token budget management

**Long-Term Memory**: Persistent SQLite storage
- Stores facts and experiences across sessions
- Queryable knowledge base

**Episodic Memory**: Experience replay
- Records complete task executions
- Enables learning from past successes/failures

**Vector Store** (Placeholder): Semantic search capability
- Blueprint for embedding-based retrieval
- Ready for ChromaDB/Pinecone integration

### 3. **State Management**

- **Checkpointing**: Save agent state at any point
- **Recovery**: Restore from previous checkpoints
- **Versioning**: Track state changes over time
- **Serialization**: Export/import state in multiple formats

### 4. **Tool System**

Tools are first-class citizens with:
- JSON Schema validation
- Error handling and retries
- Execution monitoring
- OpenAI function calling compatibility

### 5. **Observability**

- **Structured Logging**: Track every decision and action
- **Metrics Collection**: Performance and usage statistics
- **Execution Tracing**: Complete audit trail

## 🔧 Development Status

### ✅ Completed Phases

- **Phase 1**: Core Foundation
  - Basic agent loop
  - Simple tool system
  - Minimal memory
  - Basic state management

- **Phase 2**: Enhanced Loop & Planning
  - ReAct pattern implementation
  - Task planner
  - Prompt builder
  - Response parser

- **Phase 3**: Memory System
  - Long-term memory (SQLite)
  - Episodic memory
  - Vector store (placeholder)
  - Memory manager

- **Phase 4**: State & Persistence
  - State persistence
  - Checkpointing
  - Serialization
  - Versioning

- **Phase 5**: Observability (Partial)
  - Structured logging
  - Metrics collection

### 🚧 Next Steps

- **Phase 6**: Advanced Features
  - Self-reflection loops
  - Adaptive replanning
  - Enhanced error recovery

- **Phase 7**: Integrations
  - LangChain adapter
  - LlamaIndex adapter
  - Additional LLM providers

- **Phase 8**: Documentation & Polish
  - Example projects
  - Best practices guide
  - Performance optimization

## 📖 Examples

### Example 1: Multi-Step Calculation

```python
agent = Agent(llm=llm, tools=[CalculatorTool()])
result = await agent.run("Multiply 25 by 8, then add 15")

# Agent thinks:
# 1. "I need to multiply first" → calls calculator(multiply, 25, 8) → 200
# 2. "Now add 15" → calls calculator(add, 200, 15) → 215
# 3. "Final Answer: The result is 215"
```

### Example 2: With Memory & Checkpoints

```python
from state.persistence import StatePersistence

# Enable persistence
persistence = StatePersistence(backend="sqlite")
agent = Agent(llm=llm, tools=tools)

# Run task
result = await agent.run("Complex multi-step task...")

# Save checkpoint
checkpoint_id = await agent.state_manager.checkpoint(label="after_task1")

# Later: restore from checkpoint
await agent.state_manager.restore(checkpoint_id)
```

### Example 3: Querying Episodic Memory

```python
# Agent automatically stores episodes
result = await agent.run("Calculate something...")

# Later: recall similar tasks
episodes = await agent.memory.recall("calculate", memory_types=["episodic"], k=5)
for episode in episodes["episodic"]:
    print(f"Past task: {episode['task']}")
    print(f"Success: {episode['success']}")
```

## 🧪 Testing

The framework includes comprehensive tests:

- **Unit Tests**: Individual component testing
  - `test_core.py`: Agent and executor tests
  - Mock LLM for deterministic testing

- **Integration Tests**: End-to-end workflows
  - Multi-step task execution
  - Memory persistence
  - State recovery

## 🛠️ Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
# LOG_LEVEL=INFO
```

## 📊 Performance

The framework is designed for:
- **Low latency**: Efficient tool execution
- **Observability**: Full execution traces
- **Scalability**: Modular architecture
- **Reliability**: Robust error handling

## 🤝 Contributing

This is an educational framework demonstrating agent concepts. Key principles:

1. **Simplicity First**: Clear, readable code over clever abstractions
2. **Transparency**: Every decision should be observable
3. **Modularity**: Components should be independently testable
4. **Production-Ready**: Include error handling and logging from the start

## 📝 License

MIT License - Feel free to use and learn from this framework!

## 🙏 Acknowledgments

Built following best practices from:
- ReAct: Synergizing Reasoning and Acting in Language Models
- LangChain and LlamaIndex architectures
- OpenAI function calling patterns

---

**Built with ❤️ to deeply understand agent internals from first principles**
