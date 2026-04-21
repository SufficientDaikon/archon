"""Pre-step hook - Fire synapses before execution."""
import asyncio
from typing import Any


async def pre_step_hook(pipeline_executor, pipeline_state, step):
    """Fire synapses before step execution.
    
    Validates reasoning quality, checks for rationalization, etc.
    If any synapse HALTS, raises exception to block the step.
    """
    
    # Build synapse context from step
    reasoning = step.get("description", "")
    task = step.get("name", "")
    has_plan = "plan" in pipeline_state.get("accumulated", {})
    complexity = pipeline_state.get("complexity", "SIMPLE")
    
    synapse_context = {
        "reasoning": reasoning,
        "task": task,
        "has_plan": has_plan,
        "complexity": complexity,
    }
    
    # Fire synapses
    if hasattr(pipeline_executor, 'synapse_engine'):
        decisions = await pipeline_executor.synapse_engine.fire_trigger(
            "pre-execution",
            synapse_context
        )
        
        # Log decisions to pipeline state
        if "synapses" not in pipeline_state:
            pipeline_state["synapses"] = {}
        pipeline_state["synapses"]["pre_step"] = [d.to_dict() for d in decisions]
        
        # If any decision is HALT, block the step
        if any(d.is_halt for d in decisions):
            halt_msgs = [d.message for d in decisions if d.is_halt]
            raise RuntimeError(f"Pre-step synapses blocked execution: {halt_msgs}")
