"""Post-step hook - Fire synapses after execution."""
import asyncio
from typing import Any


async def post_step_hook(pipeline_executor, pipeline_state, step, output):
    """Fire synapses after step completion.
    
    Validates code quality, security, completeness, etc.
    Post-step violations are logged but don't block (informational).
    """
    
    # Build synapse context from output
    code = output.get("code", "")
    output_str = str(output)
    
    synapse_context = {
        "code": code,
        "output": output_str,
    }
    
    # Fire synapses
    if hasattr(pipeline_executor, 'synapse_engine'):
        decisions = await pipeline_executor.synapse_engine.fire_trigger(
            "post-build",
            synapse_context
        )
        
        # Log decisions to pipeline state
        if "synapses" not in pipeline_state:
            pipeline_state["synapses"] = {}
        pipeline_state["synapses"]["post_step"] = [d.to_dict() for d in decisions]
        
        # Log blocks for audit trail (don't revert)
        if any(d.is_halt for d in decisions):
            pipeline_state.setdefault("synapse_warnings", []).extend(
                [d.message for d in decisions if d.is_halt]
            )
