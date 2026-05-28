"""
Recursive descent parser — converts a pattern string into an NFA.

Supported syntax:
    A C G T     literal nucleotides
    .           any nucleotide (wildcard)
    *           zero or more  (Kleene star)
    +           one or more
    ?           zero or one
    |           alternation        e.g.  A|T
    ( )         grouping           e.g.  (ATG)+
    [ACGT]      character class    e.g.  [AC]

Grammar (EBNF):
    expr   := concat ( '|' concat )*
    concat := quant quant*
    quant  := atom ( '*' | '+' | '?' )?
    atom   := '(' expr ')' | '.' | nucleotide | '[' chars ']'
"""

from .states   import DNA_ALPHABET
from .thompson import lit, wildcard, concat, union, star, plus, question


def tokenize(pattern: str) -> list[str]:
    """
    Split a pattern into tokens.
    Handles [...] as a single token so character classes are parsed correctly.
    """
    tokens, i = [], 0
    while i < len(pattern):
        if pattern[i] == "[":
            j = pattern.index("]", i)
            tokens.append(pattern[i : j + 1])
            i = j + 1
        else:
            tokens.append(pattern[i])
            i += 1
    return tokens


def pattern_to_nfa(pattern: str):
    """
    Parse a pattern string and return a fully constructed NFA.
    Raises ValueError on invalid patterns.
    """
    tokens = tokenize(pattern)
    pos    = [0]   # mutable pointer so inner functions can advance it

    def expr():
        left = cat()
        while pos[0] < len(tokens) and tokens[pos[0]] == "|":
            pos[0] += 1
            left = union(left, cat())
        return left

    def cat():
        left = quant()
        while pos[0] < len(tokens) and tokens[pos[0]] not in ("|", ")"):
            left = concat(left, quant())
        return left

    def quant():
        base = atom()
        if pos[0] < len(tokens):
            op = tokens[pos[0]]
            if op == "*": pos[0] += 1; return star(base)
            if op == "+": pos[0] += 1; return plus(base)
            if op == "?": pos[0] += 1; return question(base)
        return base

    def atom():
        if pos[0] >= len(tokens):
            raise ValueError("Unexpected end of pattern")
        tok = tokens[pos[0]]
        pos[0] += 1

        if tok == "(":
            n = expr()
            if pos[0] >= len(tokens) or tokens[pos[0]] != ")":
                raise ValueError("Missing closing ')'")
            pos[0] += 1
            return n

        if tok == ".":
            return wildcard()

        if tok in DNA_ALPHABET:
            return lit(tok)

        if tok.startswith("["):
            chars = [c for c in tok[1:-1] if c in DNA_ALPHABET]
            if not chars:
                raise ValueError(f"Empty or invalid character class: {tok}")
            result = lit(chars[0])
            for c in chars[1:]:
                result = union(result, lit(c))
            return result

        raise ValueError(
            f"Unknown token '{tok}'. "
            f"Valid symbols: A C G T . * + ? | ( ) [ACGT]"
        )

    return expr()