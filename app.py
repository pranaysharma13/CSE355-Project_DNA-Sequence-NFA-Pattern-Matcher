"""
app.py — Streamlit UI for the DNA NFA Pattern Matcher.
This file contains only layout and interaction logic.
All theory lives in nfa_machine/  |  All visuals live in viz/

Run with:  streamlit run app.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

from nfa_machine import pattern_to_nfa, find_matches, get_steps, nfa_to_dfa, reset_counters
from viz import draw_nfa, draw_dfa, make_transition_table, nuc_html, NUC_COLORS, CSS

# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════

for key, default in [
    ("nfa", None), ("matches", []), ("steps", []),
    ("nfa_pos", None), ("dfa_start", None), ("dfa_states", []),
    ("pattern", ""), ("sequence", ""), ("ran", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════

st.set_page_config(
    page_title="DNA NFA Matcher · CSE 355",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)

PRESETS = {
    "Start codon (ATG...)":       ("ATG(A|C|G|T)+",  "GCATGAAACGATGTTGCA"),
    "Stop codons (TAA|TAG|TGA)":  ("TAA|TAG|TGA",    "ATGTCGAAATAATGCTGACCC"),
    "GC repeats":                 ("(GC)+",           "GCGCGCATCGGCGCATA"),
    "Palindrome-like [AT]..[AT]": ("[AT]..[AT]",      "ATCGATCGATAT"),
    "CpG island motif":           ("(CG)+",           "CGCGCGATCGCGATCG"),
    "Custom":                     ("",                ""),
}


# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🧬 DNA NFA Matcher")
    st.markdown("---")

    preset = st.selectbox("📂 Load a preset", list(PRESETS.keys()))
    p_pat, p_seq = PRESETS[preset]

    st.markdown("**Pattern**")
    st.markdown(
        "<small style='color:#888;font-family:monospace'>"
        "A C G T &nbsp;·&nbsp; . &nbsp;* &nbsp;+ &nbsp;? &nbsp;| &nbsp;() &nbsp;[]"
        "</small>",
        unsafe_allow_html=True,
    )
    pattern  = st.text_input("pat", value=p_pat, label_visibility="collapsed",
                              placeholder="e.g. ATG(A|C|G|T)+")

    st.markdown("**DNA Sequence**")
    sequence = st.text_input("seq", value=p_seq, label_visibility="collapsed",
                              placeholder="e.g. GCATGAAACG").upper()

    run = st.button("▶  Run Matcher", type="primary", width="stretch")

    st.markdown("---")
    st.markdown("#### 🔤 DNA Alphabet")
    labels = {"A": "Adenine", "C": "Cytosine", "G": "Guanine", "T": "Thymine"}
    for nuc, color in NUC_COLORS.items():
        st.markdown(
            f'<span style="background:{color};color:white;padding:2px 10px;'
            f'border-radius:4px;font-family:monospace;font-weight:700">{nuc}</span> '
            f'{labels[nuc]}',
            unsafe_allow_html=True,
        )
    st.markdown("---")
    st.markdown(
        "<small style='color:#aaa'>CSE 355 · Theoretical Computer Science<br>"
        "Thompson's Construction + NFA Simulation</small>",
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════
# RUN LOGIC
# ══════════════════════════════════════════════════════════

error_msg = None

if run and pattern and sequence:
    try:
        reset_counters()
        nfa     = pattern_to_nfa(pattern)
        matches = find_matches(nfa, sequence)
        steps   = get_steps(nfa, sequence)

        # Compute graph layout once; reused across all tabs to keep it stable
        import networkx as nx
        G = nx.MultiDiGraph()
        for s in sorted(nfa.all_states()): G.add_node(str(s))
        for s in nfa.all_states():
            for sym, targets in s.transitions.items():
                for t in targets: G.add_edge(str(s), str(t))
        nfa_pos = nx.spring_layout(G, seed=42, k=2.2)

        dfa_start, dfa_states = nfa_to_dfa(nfa)

        st.session_state.update({
            "nfa": nfa, "matches": matches, "steps": steps, "nfa_pos": nfa_pos,
            "dfa_start": dfa_start, "dfa_states": dfa_states,
            "pattern": pattern, "sequence": sequence, "ran": True,
        })
    except Exception as e:
        error_msg = str(e)

if error_msg:
    st.error(f"⚠️ Pattern error: {error_msg}")

# ══════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════

st.markdown("""
<div class="dna-header">
  <p class="dna-title">🧬 DNA Sequence Pattern Matcher</p>
  <p class="dna-subtitle">NFA · Thompson's Construction · Subset Construction · CSE 355</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.ran:
    st.info("👈  Choose a preset or enter a pattern and sequence, then click **Run Matcher**.")

# ══════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📖 Theory", "🔬 NFA Diagram", "🎯 Matching", "🎬 Step-by-Step", "⚙️ NFA → DFA",
])

# ── Tab 1: Theory ────────────────────────────────────────
with tab1:
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("### What is an NFA?")
        st.markdown("""<div class="theory-box"><h4>Nondeterministic Finite Automaton</h4>
An NFA is a 5-tuple <b>M = (Q, Σ, δ, q₀, F)</b> where multiple transitions on the
same symbol are allowed, and ε-transitions (free moves) are permitted.<br><br>
The machine <b>simultaneously explores all possible paths</b>.
A string is <b>accepted</b> if <i>any</i> path leads to an accept state.
</div>""", unsafe_allow_html=True)

        st.markdown("#### Formal Definition")
        st.latex(r"M = (Q,\ \Sigma,\ \delta,\ q_0,\ F)")
        st.latex(r"\delta : Q \times (\Sigma \cup \{\varepsilon\}) \rightarrow 2^Q")

        if st.session_state.ran:
            nfa    = st.session_state.nfa
            states = sorted(nfa.all_states())
            st.markdown(f"#### For pattern `{st.session_state.pattern}`")
            st.markdown(f"- **Q** = {{ {', '.join(str(s) for s in states)} }}")
            st.markdown(f"- **Σ** = {{ A, C, G, T, ε }}")
            st.markdown(f"- **q₀** = {nfa.start}  &nbsp; **F** = {{ {nfa.accept} }}")
            st.markdown(f"- **|Q|** = {len(states)} states")

    with col_r:
        st.markdown("### Thompson's Construction")
        st.markdown("""<div class="theory-box"><h4>Building an NFA from a pattern (bottom-up)</h4>
<b>lit(A)</b> → 2 states, one labeled transition<br>
<b>concat(n1, n2)</b> → ε-link from n1's accept to n2's start<br>
<b>union(n1|n2)</b> → new start/accept with ε-branches to both<br>
<b>star(n*)</b> → loop-back + skip-ahead via ε-transitions<br>
<b>wildcard(.)</b> → transitions on all 4 nucleotides<br><br>
Each operator is implemented in <code>nfa_machine/thompson.py</code>.
</div>""", unsafe_allow_html=True)

        st.markdown("### ε-closure Simulation")
        st.markdown("""<div class="theory-box"><h4>How the NFA is simulated</h4>
Track a <b>set of active states</b> (not just one):<br><br>
1. Start: ε-closure({q₀})<br>
2. For each symbol c: compute <b>move</b>(S, c), then take its ε-closure<br>
3. Accept if active set ∩ F ≠ ∅<br><br>
Implemented in <code>nfa_machine/simulate.py</code>.
</div>""", unsafe_allow_html=True)

        st.markdown("### Why DNA?")
        st.markdown("""<div class="theory-box"><h4>Bioinformatics connection</h4>
DNA is a string over {A, C, G, T}. Finding gene features (start codons, stop codons,
repeat regions) is exactly a pattern-matching problem. NFA handles ambiguous patterns
naturally via nondeterminism — just like biological sequence variability.
</div>""", unsafe_allow_html=True)


# ── Tab 2: NFA Diagram ───────────────────────────────────
with tab2:
    if not st.session_state.ran:
        st.info("Run the matcher first.")
    else:
        nfa = st.session_state.nfa
        col_g, col_t = st.columns([3, 2])
        with col_g:
            st.markdown(f"#### NFA for `{st.session_state.pattern}`")
            fig, ax = plt.subplots(figsize=(9, 6))
            draw_nfa(nfa, ax=ax, pos=st.session_state.nfa_pos,
                     title=f"NFA — {len(nfa.all_states())} states")
            plt.tight_layout()
            st.pyplot(fig, width="stretch")
            plt.close(fig)

        with col_t:
            st.markdown("#### Transition Table δ")
            st.dataframe(make_transition_table(nfa), width="stretch", hide_index=True)
            st.markdown("""<div class="theory-box" style="margin-top:1rem">
▶ = start &nbsp;|&nbsp; ✓ = accept &nbsp;|&nbsp; ∅ = no transition<br>
Each cell is a <i>set</i> of states — this is what makes it an NFA.
</div>""", unsafe_allow_html=True)


# ── Tab 3: Matching Results ──────────────────────────────
with tab3:
    if not st.session_state.ran:
        st.info("Run the matcher first.")
    else:
        matches  = st.session_state.matches
        sequence = st.session_state.sequence

        match_pos = set()
        for s, e in matches: match_pos.update(range(s, e))
        coverage  = round(len(match_pos) / len(sequence) * 100, 1) if sequence else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Matches",         len(matches))
        m2.metric("Sequence length", len(sequence))
        m3.metric("Matched bases",   len(match_pos))
        m4.metric("Coverage",        f"{coverage}%")

        st.markdown("#### Highlighted Sequence")
        st.markdown(nuc_html(sequence, highlight=match_pos), unsafe_allow_html=True)
        st.markdown(
            "<small style='color:#888'>🟡 Yellow outline = matched nucleotide</small>",
            unsafe_allow_html=True,
        )

        st.markdown("#### Match Details")
        if matches:
            for i, (s, e) in enumerate(matches, 1):
                boxes = "".join(
                    f'<span style="background:{NUC_COLORS.get(c,"#888")};color:white;'
                    f'padding:1px 6px;border-radius:4px;font-family:monospace;'
                    f'font-weight:700;margin:1px">{c}</span>'
                    for c in sequence[s:e]
                )
                st.markdown(
                    f'<div class="match-card">Match {i}: &nbsp;{boxes}'
                    f'&nbsp;&nbsp; positions [{s} : {e}]</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="no-match-card">No matches found.</div>',
                unsafe_allow_html=True,
            )


# ── Tab 4: Step-by-Step ──────────────────────────────────
with tab4:
    if not st.session_state.ran:
        st.info("Run the matcher first.")
    else:
        steps    = st.session_state.steps
        nfa      = st.session_state.nfa
        sequence = st.session_state.sequence

        st.markdown(
            "Use the slider to step through execution one character at a time. "
            "**Red nodes** = currently active states."
        )
        step = st.slider("Step", 0, len(steps) - 1, 0, format="Step %d")
        char_idx, char_read, active = steps[step]

        badge = (
            "Step 0 · Initial ε-closure (before any input)"
            if char_read == "—"
            else f"Step {step} · Read '{char_read}' at position {char_idx}"
        )
        st.markdown(f'<div class="step-badge">{badge}</div>', unsafe_allow_html=True)

        col_g, col_i = st.columns([3, 2])
        with col_g:
            fig, ax = plt.subplots(figsize=(8, 5.5))
            draw_nfa(nfa, active=active, ax=ax, pos=st.session_state.nfa_pos,
                     title=f"Active states — step {step}")
            plt.tight_layout()
            st.pyplot(fig, width="stretch")
            plt.close(fig)

        with col_i:
            st.markdown("#### Active States")
            for s in sorted(active):
                flags = ("▶ " if s == nfa.start else "") + ("✓" if s.is_accept else "")
                st.markdown(
                    f'<div style="background:{__import__("viz").NODE_COLORS["active"]};'
                    f'color:white;padding:6px 14px;border-radius:8px;margin:4px 0;'
                    f'font-family:monospace;font-weight:700">{s} {flags}</div>',
                    unsafe_allow_html=True,
                )
            if not active:
                st.markdown('<div class="reject-badge">Dead — no active states</div>',
                            unsafe_allow_html=True)

            is_acc = any(s.is_accept for s in active)
            st.markdown("")
            st.markdown(
                f'<div class="{"accept" if is_acc else "reject"}-badge">'
                f'{"✓ Accept reachable" if is_acc else "✗ No accept state active"}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"\n**{len(active)}** states active simultaneously")
            st.markdown("""<div class="theory-box" style="margin-top:0.5rem">
A DFA would have exactly <b>1</b> active state here.
Multiple active states = nondeterminism in action.
</div>""", unsafe_allow_html=True)

        st.markdown("#### Sequence Progress")
        st.markdown(
            nuc_html(sequence, active_idx=char_idx if char_idx >= 0 else None),
            unsafe_allow_html=True,
        )


# ── Tab 5: NFA → DFA ─────────────────────────────────────
with tab5:
    if not st.session_state.ran:
        st.info("Run the matcher first.")
    else:
        nfa        = st.session_state.nfa
        dfa_start  = st.session_state.dfa_start
        dfa_states = st.session_state.dfa_states
        n_nfa      = len(nfa.all_states())
        n_dfa      = len(dfa_states)

        c1, c2, c3 = st.columns(3)
        c1.metric("NFA states",       n_nfa)
        c2.metric("DFA states",       n_dfa)
        c3.metric("Worst-case bound", f"2^{n_nfa} = {2**n_nfa}")

        st.markdown("---")
        col_n, col_d = st.columns(2)

        with col_n:
            st.markdown(f"#### NFA  ({n_nfa} states)")
            fig1, ax1 = plt.subplots(figsize=(7, 5.5))
            draw_nfa(nfa, ax=ax1, pos=st.session_state.nfa_pos, title="NFA")
            plt.tight_layout()
            st.pyplot(fig1, width="stretch")
            plt.close(fig1)

        with col_d:
            st.markdown(f"#### DFA  ({n_dfa} states)")
            fig2, ax2 = plt.subplots(figsize=(7, 5.5))
            draw_dfa(dfa_start, dfa_states, ax=ax2,
                     title=f"DFA via Subset Construction ({n_dfa} states)")
            plt.tight_layout()
            st.pyplot(fig2, width="stretch")
            plt.close(fig2)

        st.markdown("#### DFA Transition Table")
        import pandas as pd
        rows = []
        for ds in dfa_states:
            row = {"DFA State": ds.label()
                                + (" ▶" if ds == dfa_start else "")
                                + (" ✓" if ds.is_accept else "")}
            for ch in sorted({"A", "C", "G", "T"}):
                t = ds.transitions.get(ch)
                row[ch] = t.label() if t else "∅"
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

        with st.expander("📚 How subset construction works"):
            st.markdown("""
**Each DFA state = a *set* of NFA states** (its ε-closure).

**Algorithm:**
1. Start DFA state = ε-closure({q₀})
2. For each DFA state S and symbol c: next state = ε-closure(move(S, c))
3. A DFA state is accept if it contains any NFA accept state

**Key theorem:** NFA = DFA in expressive power, but DFA may need up to 2ⁿ states.
This is why NFA is preferred for pattern construction — it's always compact.

Implemented in `nfa_machine/subset.py`.
""")