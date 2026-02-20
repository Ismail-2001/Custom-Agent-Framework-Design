import pytest
import os
from state.manager import StateManager, TaskStatus
from state.persistence import StatePersistence

@pytest.mark.asyncio
async def test_state_manager_basics():
    manager = StateManager(task="Initial Task")
    assert manager.get_state().task == "Initial Task"
    assert manager.get_state().status == TaskStatus.PENDING
    
    manager.update_status(TaskStatus.RUNNING)
    manager.add_history("thought", "I am starting")
    
    state = manager.get_state()
    assert state.status == TaskStatus.RUNNING
    assert len(state.history) == 1
    assert state.history[0]["event"] == "thought"

@pytest.mark.asyncio
async def test_persistence_sqlite(tmp_path):
    db_path = str(tmp_path / "test_persistence.db")
    persistence = StatePersistence(backend="sqlite", db_path=db_path)
    
    manager = StateManager(task="Persistent Task")
    manager.add_history("thought", "Saving this")
    
    # Save checkpoint
    checkpoint_id = await persistence.save(manager.get_state(), label="v1")
    assert checkpoint_id is not None
    
    # Modify current state
    manager.update_status(TaskStatus.COMPLETED)
    
    # Restore
    restored_state = await persistence.load(checkpoint_id)
    assert restored_state.task == "Persistent Task"
    assert restored_state.status == TaskStatus.PENDING # Initial status when saved
    assert len(restored_state.history) == 1

@pytest.mark.asyncio
async def test_list_checkpoints(tmp_path):
    db_path = str(tmp_path / "test_list_checkpoints.db")
    persistence = StatePersistence(backend="sqlite", db_path=db_path)
    
    manager = StateManager(task="Checkpoint List Task")
    await persistence.save(manager.get_state(), label="first")
    await persistence.save(manager.get_state(), label="second")
    
    checkpoints = await persistence.list_checkpoints()
    assert len(checkpoints) == 2
    # The label is now stored and returned correctly
    assert checkpoints[0]["label"] == "second" # Latest first
