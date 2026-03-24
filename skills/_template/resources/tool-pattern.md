# Async Generator Tool Pattern

This document describes the async generator tool pattern from Vercel's Knowledge Agent Template for real-time tool visualization and streaming updates.

## Overview

The async generator pattern enables tools to report progress in real-time as they execute, providing:

- **Loading states**: Show "Processing..." before results
- **Progress updates**: Stream intermediate results
- **Done/Error states**: Clear completion signals
- **Better UX**: Users see what's happening instead of waiting for completion

## Pattern Structure

### Python Implementation

```python
from typing import AsyncGenerator, Literal
from dataclasses import dataclass


@dataclass
class ToolStatus:
    """Status update from a tool."""
    status: Literal['loading', 'processing', 'done', 'error']
    message: str
    data: dict = None


async def my_tool(param: str) -> AsyncGenerator[ToolStatus, None]:
    """
    Example tool using async generator pattern.

    Yields status updates as it progresses.
    Final yield is 'done' or 'error'.
    """
    # Step 1: Loading
    yield ToolStatus(
        status='loading',
        message=f'Starting operation for {param}...'
    )

    # Step 2: Processing (can yield multiple times)
    yield ToolStatus(
        status='processing',
        message='Fetching data...'
    )

    # Simulate work
    data = await fetch_data(param)

    yield ToolStatus(
        status='processing',
        message=f'Processing {len(data)} items...'
    )

    # More work
    result = await process_data(data)

    # Step 3: Done
    yield ToolStatus(
        status='done',
        message=f'Completed successfully',
        data={'result': result, 'count': len(data)}
    )


# Usage
async for status in my_tool('example'):
    if status.status == 'loading':
        print(f"⏳ {status.message}")
    elif status.status == 'processing':
        print(f"🔄 {status.message}")
    elif status.status == 'done':
        print(f"✅ {status.message}")
        print(f"Result: {status.data}")
    elif status.status == 'error':
        print(f"❌ {status.message}")
```

### TypeScript Implementation

```typescript
type ToolStatus =
  | { status: "loading"; message: string }
  | { status: "processing"; message: string; progress?: number }
  | { status: "done"; message: string; data?: any }
  | { status: "error"; message: string; error?: Error };

async function* myTool(param: string): AsyncGenerator<ToolStatus> {
  // Step 1: Loading
  yield {
    status: "loading",
    message: `Starting operation for ${param}...`,
  };

  // Step 2: Processing
  yield {
    status: "processing",
    message: "Fetching data...",
    progress: 0.3,
  };

  const data = await fetchData(param);

  yield {
    status: "processing",
    message: `Processing ${data.length} items...`,
    progress: 0.7,
  };

  const result = await processData(data);

  // Step 3: Done
  yield {
    status: "done",
    message: "Completed successfully",
    data: { result, count: data.length },
  };
}

// Usage
for await (const status of myTool("example")) {
  switch (status.status) {
    case "loading":
      console.log(`⏳ ${status.message}`);
      break;
    case "processing":
      console.log(`🔄 ${status.message} (${status.progress * 100}%)`);
      break;
    case "done":
      console.log(`✅ ${status.message}`);
      console.log("Result:", status.data);
      break;
    case "error":
      console.error(`❌ ${status.message}`);
      break;
  }
}
```

## State Transitions

Valid state flow:

```
loading → processing → processing → ... → done
                                      ↘ error

OR

loading → done (fast operations)
loading → error (immediate failure)
```

**Rules**:

- Must start with `loading`
- Can have 0+ `processing` states
- Must end with either `done` or `error`
- Cannot transition back to earlier states

## Command Output Format

When tools execute shell commands, stream output in chunks:

```python
async def execute_command(cmd: str) -> AsyncGenerator[ToolStatus, None]:
    """Execute command and stream output."""
    yield ToolStatus(status='loading', message=f'Running: {cmd}')

    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Stream stdout in real-time
    async for line in process.stdout:
        yield ToolStatus(
            status='processing',
            message=line.decode().strip()
        )

    # Wait for completion
    return_code = await process.wait()

    if return_code == 0:
        yield ToolStatus(
            status='done',
            message=f'Command completed (exit code 0)',
            data={'exit_code': return_code}
        )
    else:
        stderr = await process.stderr.read()
        yield ToolStatus(
            status='error',
            message=f'Command failed (exit code {return_code})',
            data={'exit_code': return_code, 'stderr': stderr.decode()}
        )
```

## Frontend Integration Pattern

### React Component

```tsx
import { useState, useEffect } from "react";

interface ToolVisualizerProps {
  tool: () => AsyncGenerator<ToolStatus>;
}

export function ToolVisualizer({ tool }: ToolVisualizerProps) {
  const [status, setStatus] = useState<ToolStatus>({
    status: "loading",
    message: "Initializing...",
  });

  useEffect(() => {
    (async () => {
      for await (const update of tool()) {
        setStatus(update);
      }
    })();
  }, [tool]);

  return (
    <div className="tool-status">
      {status.status === "loading" && (
        <div className="loading">
          <Spinner />
          <span>{status.message}</span>
        </div>
      )}

      {status.status === "processing" && (
        <div className="processing">
          <ProgressBar value={status.progress} />
          <span>{status.message}</span>
        </div>
      )}

      {status.status === "done" && (
        <div className="done">
          <CheckIcon />
          <span>{status.message}</span>
          {status.data && <pre>{JSON.stringify(status.data, null, 2)}</pre>}
        </div>
      )}

      {status.status === "error" && (
        <div className="error">
          <ErrorIcon />
          <span>{status.message}</span>
        </div>
      )}
    </div>
  );
}
```

## Multi-Tool Orchestration

When orchestrating multiple tools:

```python
async def multi_tool_workflow() -> AsyncGenerator[ToolStatus, None]:
    """Run multiple tools in sequence, streaming all updates."""

    # Tool 1
    yield ToolStatus(status='loading', message='Phase 1: Fetching data')
    async for status in fetch_data_tool():
        yield status

    # Tool 2
    yield ToolStatus(status='loading', message='Phase 2: Processing')
    async for status in process_tool():
        yield status

    # Tool 3
    yield ToolStatus(status='loading', message='Phase 3: Validation')
    async for status in validate_tool():
        yield status

    yield ToolStatus(status='done', message='All phases complete')
```

## Error Handling

Proper error handling with async generators:

```python
async def robust_tool(param: str) -> AsyncGenerator[ToolStatus, None]:
    """Tool with comprehensive error handling."""
    yield ToolStatus(status='loading', message='Starting...')

    try:
        yield ToolStatus(status='processing', message='Step 1')
        data = await risky_operation_1()

        yield ToolStatus(status='processing', message='Step 2')
        result = await risky_operation_2(data)

        yield ToolStatus(
            status='done',
            message='Success',
            data={'result': result}
        )

    except ValueError as e:
        yield ToolStatus(
            status='error',
            message=f'Invalid input: {str(e)}'
        )
    except TimeoutError:
        yield ToolStatus(
            status='error',
            message='Operation timed out'
        )
    except Exception as e:
        yield ToolStatus(
            status='error',
            message=f'Unexpected error: {str(e)}'
        )
```

## Progress Reporting

Include progress percentages for long operations:

```python
async def long_operation(items: list) -> AsyncGenerator[ToolStatus, None]:
    """Process many items with progress reporting."""
    yield ToolStatus(status='loading', message=f'Processing {len(items)} items')

    for i, item in enumerate(items):
        progress = (i + 1) / len(items)
        yield ToolStatus(
            status='processing',
            message=f'Processing item {i+1}/{len(items)}',
            data={'progress': progress}
        )
        await process_item(item)

    yield ToolStatus(status='done', message='All items processed')
```

## Integration with Archon

To add async generator pattern to an Archon skill:

```python
# In skill implementation
from archon.tools import ToolStatus

async def my_skill_tool(param: str) -> AsyncGenerator[ToolStatus, None]:
    """Archon skill with async generator pattern."""

    # Follow SKILL.md workflow
    yield ToolStatus(status='loading', message='Step 1: [Step name from SKILL.md]')
    # Execute step 1

    yield ToolStatus(status='processing', message='Step 2: [Step name]')
    # Execute step 2

    # ... continue for all workflow steps

    yield ToolStatus(
        status='done',
        message='Skill execution complete',
        data={'output': 'formatted per SKILL.md Output Format section'}
    )
```

## Testing Async Generator Tools

```python
import pytest

@pytest.mark.asyncio
async def test_tool_with_generator():
    """Test async generator tool."""
    statuses = []

    async for status in my_tool('test-param'):
        statuses.append(status.status)

    # Verify state transitions
    assert statuses[0] == 'loading'
    assert statuses[-1] in ['done', 'error']

    # Verify no invalid transitions
    for i in range(len(statuses) - 1):
        current, next = statuses[i], statuses[i+1]
        assert is_valid_transition(current, next)
```

## Best Practices

### DO:

- Always start with `loading` state
- Always end with `done` or `error` state
- Provide meaningful messages at each step
- Include progress percentages for long operations
- Stream command output in real-time
- Handle all exceptions and yield error states
- Keep processing messages concise
- Include final data in `done` state

### DON'T:

- Skip the loading state
- Forget to yield final done/error state
- Leave tools hanging without completion
- Yield too frequently (causes UI thrashing)
- Include sensitive data in status messages
- Transition backwards (error → processing)
- Yield after done/error state

## Comparison with Traditional Tools

**Traditional (blocking)**:

```python
def old_tool(param: str) -> dict:
    # User sees nothing until completion
    data = fetch_data(param)
    result = process_data(data)
    return {'result': result}
```

**Async Generator (streaming)**:

```python
async def new_tool(param: str) -> AsyncGenerator[ToolStatus, None]:
    yield ToolStatus(status='loading', message='Starting...')
    yield ToolStatus(status='processing', message='Fetching...')
    data = await fetch_data(param)
    yield ToolStatus(status='processing', message='Processing...')
    result = await process_data(data)
    yield ToolStatus(status='done', data={'result': result})
```

**Benefits**:

- ✅ Real-time visibility
- ✅ Better perceived performance
- ✅ Can cancel mid-execution
- ✅ Users know progress, not just waiting
- ✅ Easier debugging (see where failures occur)

---

**Adopt this pattern for all long-running tools in Archon to provide excellent real-time UX.**
