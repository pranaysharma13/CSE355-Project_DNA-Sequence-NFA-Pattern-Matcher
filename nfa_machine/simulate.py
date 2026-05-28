"""
NFA simulation using ε-closure and move operations.

The core idea: instead of tracking one active state (like a DFA),
we track a *set* of active states and advance all of them simultaneously.
This is nondeterminism in action.
"""

from .states import NFA, EPSILON


def eps_closure(states: set) -> frozenset:
    """
    Compute the ε-closure of a set of NFA states.
    i.e. all states reachable from `states` by following ε-transitions only.
    """
    closure, stack = set(states), list(states)
    while stack:
        for nxt in stack.pop().transitions.get(EPSILON, set()):
            if nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
    return frozenset(closure)


def move(states: frozenset, symbol: str) -> set:
    """
    Compute move(states, symbol):
    all NFA states reachable from `states` by consuming `symbol`.
    """
    result = set()
    for s in states:
        result |= s.transitions.get(symbol, set())
    return result


def find_matches(nfa: NFA, text: str) -> list[tuple[int, int]]:
    """
    Find all non-overlapping, leftmost-longest matches in `text`.
    Returns a list of (start, end) index pairs.

    Algorithm: for each starting position, simulate the NFA greedily
    and record the furthest accept state reached.
    """
    matches = []
    i = 0
    while i < len(text):
        current    = eps_closure({nfa.start})
        last_match = None
        for j in range(i, len(text)):
            current = eps_closure(move(current, text[j]))
            if not current:
                break
            if any(s.is_accept for s in current):
                last_match = j + 1      # record furthest accept
        if last_match:
            matches.append((i, last_match))
            i = last_match              # skip past matched region
        else:
            i += 1
    return matches


def get_steps(nfa: NFA, text: str) -> list[tuple[int, str, frozenset]]:
    """
    Produce a full step-by-step execution trace for visualization.

    Returns a list of (char_index, char_read, active_states):
      - Step 0:  (-1, "—", initial ε-closure)   — before any input
      - Step i:  (i-1, text[i-1], active states after reading text[i-1])
    """
    current = eps_closure({nfa.start})
    steps   = [(-1, "—", current)]
    for i, ch in enumerate(text):
        current = eps_closure(move(current, ch))
        steps.append((i, ch, current))
    return steps