import pytest
import asyncio
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.vector_store import VectorStoreMemory
from memory.manager import MemoryManager

@pytest.mark.asyncio
async def test_short_term_memory():
    memory = ShortTermMemory(max_tokens=100)
    await memory.add_message("System prompt", role="system")
    await memory.add_message("User query", role="user")
    
    messages = await memory.get_messages()
    assert len(messages) == 2
    assert messages[0].role == "system"
    assert messages[1].content == "User query"
    
    await memory.clear()
    messages = await memory.get_messages()
    assert len(messages) == 0

@pytest.mark.asyncio
async def test_vector_store_memory():
    store = VectorStoreMemory()
    await store.store("Test 1", [1.0, 0.0, 0.0])
    await store.store("Test 2", [0.0, 1.0, 0.0])
    
    # Query for Test 1
    results = await store.retrieve([0.9, 0.1, 0.0], k=1)
    assert len(results) == 1
    assert results[0]["content"] == "Test 1"
    assert results[0]["similarity"] > 0.8

@pytest.mark.asyncio
async def test_memory_manager_integration():
    manager = MemoryManager()
    # Test adding a task and recalling it
    await manager.remember("How to bake a cake?", role="user")
    await manager.remember("First, preheat the oven.", role="assistant")
    
    # Simple check on short term
    st_messages = await manager.short_term.get_messages()
    assert len(st_messages) == 2
    
    # Episodic storage logic (usually triggered by agent)
    await manager.add_episode(
        task="Test Task",
        steps=[],
        success=True,
        final_answer="Done",
        duration=1.0
    )
    
    # Recall (this typically queries multiple bases)
    # Since our search is currently basic, we just check it doesn't crash
    results = await manager.recall("Test")
    assert isinstance(results, dict)
    assert "episodic" in results
