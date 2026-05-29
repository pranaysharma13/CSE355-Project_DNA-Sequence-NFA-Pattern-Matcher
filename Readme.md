# DNA Sequence NFA Pattern Matcher
### CSE 355 — Theoretical Computer Science

---

## Setup & Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Project Structure

```
project/
├── app.py                  ← Streamlit UI only (layout + interaction)
│
├── nfa/                    ← All automata theory
│   ├── __init__.py         ← Public API
│   ├── states.py           ← NFAState, NFA, DFAState data structures
│   ├── thompson.py         ← Thompson's Construction (one fn per operator)
│   ├── parser.py           ← Recursive descent parser: pattern → NFA
│   ├── simulate.py         ← ε-closure, move, find_matches, get_steps
│   └── subset.py           ← Subset construction: NFA → DFA
│
├── viz/                    ← All visualization
│   ├── __init__.py         ← Public API
│   ├── graphs.py           ← draw_nfa, draw_dfa, transition table
│   ├── sequence.py         ← HTML nucleotide renderer + color constants
│   └── styles.py           ← Global CSS string
│
└── requirements.txt
```

### Why this structure?
| File | Responsibility |
|---|---|
| `app.py` | Streamlit layout, user interaction |
| `nfa/states.py` | Data structures only |
| `nfa/thompson.py` | One function per operator |
| `nfa/parser.py` | Grammar + recursive descent |
| `nfa/simulate.py` | ε-closure + matching |
| `nfa/subset.py` | Subset construction |
| `viz/graphs.py` | Matplotlib diagrams |
| `viz/sequence.py` | HTML rendering |
| `viz/styles.py` | CSS constants |

Each file has one clear job.

---

## Pattern Syntax

| Symbol | Meaning | DNA Example |
|---|---|---|
| `A C G T` | Literal nucleotide | `ATG` |
| `.` | Any nucleotide | `A.G` |
| `*` | Zero or more | `(GC)*` |
| `+` | One or more | `(AT)+` |
| `?` | Zero or one | `A?T` |
| `\|` | Alternation | `TAA\|TAG\|TGA` |
| `()` | Grouping | `(ATG)+` |
| `[ACGT]` | Character class | `[AC]` |

---

## Theory Connections

```
Pattern string
    ↓  parser.py  (recursive descent)
NFA (Thompson's Construction)
    ↓  simulate.py  (ε-closure + move)
Match positions in DNA sequence
    ↓  subset.py  (subset construction)
Equivalent DFA
```

Formal NFA definition:
```
M = (Q, Σ, δ, q₀, F)
δ : Q × (Σ ∪ {ε}) → 2^Q
```

Key theorem demonstrated: **NFA ≡ DFA** in expressive power,
but DFA may need up to 2^n states vs NFA's n states.