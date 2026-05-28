"""
Subset Construction — converts an NFA to an equivalent DFA.

Key insight: each DFA state represents a *set* of NFA states (the ε-closure).
A DFA state is an accept state if it contains any NFA accept state.

Worst-case: 2^n DFA states for an NFA with n states.
In practice, far fewer states are reachable.
"""

from collections import deque
from .states   import NFA, DFAState, DNA_ALPHABET
from .simulate import eps_closure, move


def nfa_to_dfa(nfa: NFA) -> tuple[DFAState, list[DFAState]]:
    """
    Run subset construction on the given NFA.

    Returns:
        start_dfa  — the DFA's start state
        all_states — list of all reachable DFA states
    """
    # Initial DFA state = ε-closure of the NFA start state
    s0    = eps_closure({nfa.start})
    start = DFAState(s0)
    table = {s0: start}   # frozenset[NFAState] → DFAState
    queue = deque([s0])

    while queue:
        subset    = queue.popleft()
        dfa_state = table[subset]

        for ch in sorted(DNA_ALPHABET):
            next_set = eps_closure(move(subset, ch))
            if not next_set:
                continue                       # dead transition — omit
            if next_set not in table:
                table[next_set] = DFAState(next_set)
                queue.append(next_set)
            dfa_state.transitions[ch] = table[next_set]

    return start, list(table.values())