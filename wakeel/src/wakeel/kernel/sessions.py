from __future__ import annotations

from collections import deque
from typing import Protocol, runtime_checkable

MessageDict = dict[str, str]


@runtime_checkable
class SessionStore(Protocol):
    def get_history(self, session_id: str) -> list[MessageDict]: ...
    def append(self, session_id: str, role: str, content: str) -> None: ...
    def clear(self, session_id: str) -> None: ...


class InMemorySessionStore:
    """Rolling window of the last max_turns conversation turns."""

    def __init__(self, max_turns: int = 10) -> None:
        self._max_messages = max_turns * 2
        self._sessions: dict[str, deque[MessageDict]] = {}

    def _get(self, session_id: str) -> deque[MessageDict]:
        if session_id not in self._sessions:
            self._sessions[session_id] = deque(maxlen=self._max_messages)
        return self._sessions[session_id]

    def get_history(self, session_id: str) -> list[MessageDict]:
        return list(self._get(session_id))

    def append(self, session_id: str, role: str, content: str) -> None:
        self._get(session_id).append({"role": role, "content": content})

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
