"""
Thompson's Construction — builds NFA fragments for each pattern operator.

Each function takes NFA fragment(s) and returns a new NFA.
Fragments are composed bottom-up by the parser.

Reference: Ken Thompson, "Regular Expression Search Algorithm" (1968)
"""

from .states import NFAState, NFA, DNA_ALPHABET, EPSILON


def _fresh() -> tuple[NFAState, NFAState]:
    """Allocate a fresh (start, accept) pair for a new fragment."""
    return NFAState(), NFAState()


def lit(char: str) -> NFA:
    """
    Literal nucleotide match.
    Fragment:  s0 --char--> s1
    """
    s, a = _fresh()
    s.add_transition(char, a)
    return NFA(s, a)


def wildcard() -> NFA:
    """
    Dot operator — matches any single nucleotide (A, C, G, or T).
    Fragment:  s0 --A,C,G,T--> s1
    """
    s, a = _fresh()
    for c in DNA_ALPHABET:
        s.add_transition(c, a)
    return NFA(s, a)


def concat(n1: NFA, n2: NFA) -> NFA:
    """
    Concatenation — n1 followed by n2.
    Links accept of n1 to start of n2 via ε.
    Fragment:  [n1] --ε--> [n2]
    """
    n1.accept.is_accept = False
    n1.accept.add_transition(EPSILON, n2.start)
    return NFA(n1.start, n2.accept)


def union(n1: NFA, n2: NFA) -> NFA:
    """
    Alternation — n1 | n2.
    New start ε-branches into both; both connect to new accept via ε.
    Fragment:  s0 --ε--> [n1] --ε--> a1
               s0 --ε--> [n2] --ε--> a1
    """
    s, a = _fresh()
    s.add_transition(EPSILON, n1.start)
    s.add_transition(EPSILON, n2.start)
    n1.accept.is_accept = False
    n2.accept.is_accept = False
    n1.accept.add_transition(EPSILON, a)
    n2.accept.add_transition(EPSILON, a)
    return NFA(s, a)


def star(n: NFA) -> NFA:
    """
    Kleene star — zero or more repetitions.
    Fragment:  s0 --ε--> [n] --ε--> s0  (loop)
               s0 --ε--> a1             (skip)
    """
    s, a = _fresh()
    s.add_transition(EPSILON, n.start)
    s.add_transition(EPSILON, a)
    n.accept.is_accept = False
    n.accept.add_transition(EPSILON, n.start)  # loop back
    n.accept.add_transition(EPSILON, a)
    return NFA(s, a)


def plus(n: NFA) -> NFA:
    """
    Plus — one or more repetitions (must enter at least once).
    Fragment:  s0 --ε--> [n] --ε--> [n]  (loop, no skip)
    """
    s, a = _fresh()
    s.add_transition(EPSILON, n.start)
    n.accept.is_accept = False
    n.accept.add_transition(EPSILON, n.start)  # loop back
    n.accept.add_transition(EPSILON, a)
    return NFA(s, a)


def question(n: NFA) -> NFA:
    """
    Question mark — zero or one occurrence.
    Fragment:  s0 --ε--> [n] --ε--> a1
               s0 --ε--> a1          (skip)
    """
    s, a = _fresh()
    s.add_transition(EPSILON, n.start)
    s.add_transition(EPSILON, a)
    n.accept.is_accept = False
    n.accept.add_transition(EPSILON, a)
    return NFA(s, a)