"""
Core data structures: NFAState, NFA, DFAState.
All state IDs are auto-assigned and globally unique within a run.
Call reset_counters() before building a new NFA to restart IDs from 0.
"""

from collections import defaultdict, deque

EPSILON      = "ε"
DNA_ALPHABET = {"A", "C", "G", "T"}


class NFAState:
    _counter = 0

    def __init__(self):
        self.id = NFAState._counter
        NFAState._counter += 1
        self.transitions: dict[str, set["NFAState"]] = defaultdict(set)
        self.is_accept = False

    def add_transition(self, symbol: str, target: "NFAState"):
        self.transitions[symbol].add(target)

    def __repr__(self):  return f"q{self.id}"
    def __hash__(self):  return hash(self.id)
    def __eq__(self, o): return isinstance(o, NFAState) and self.id == o.id
    def __lt__(self, o): return self.id < o.id


class NFA:
    def __init__(self, start: NFAState, accept: NFAState):
        self.start  = start
        self.accept = accept
        accept.is_accept = True

    def all_states(self) -> set[NFAState]:
        """BFS to collect every reachable state."""
        visited, queue = set(), deque([self.start])
        while queue:
            s = queue.popleft()
            if s in visited:
                continue
            visited.add(s)
            for targets in s.transitions.values():
                queue.extend(t for t in targets if t not in visited)
        return visited


class DFAState:
    _counter = 0

    def __init__(self, subset: frozenset[NFAState]):
        self.id = DFAState._counter
        DFAState._counter += 1
        self.subset = subset
        self.transitions: dict[str, "DFAState"] = {}
        self.is_accept = any(s.is_accept for s in subset)

    def label(self) -> str:
        """Human-readable label showing the NFA states this DFA state represents."""
        ids = sorted(s.id for s in self.subset)
        return "{" + ",".join(f"q{i}" for i in ids) + "}"


def reset_counters():
    """Reset state ID counters to 0. Call before building a new NFA."""
    NFAState._counter = 0
    DFAState._counter = 0