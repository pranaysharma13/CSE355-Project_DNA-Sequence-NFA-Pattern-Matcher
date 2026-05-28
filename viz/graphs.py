"""
Graph visualization for NFA and DFA using networkx + matplotlib.
Kept separate from the Streamlit UI so diagrams can also be used in scripts.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import pandas as pd

from .sequence import NODE_COLORS
from nfa_machine.states import NFA, DFAState, DNA_ALPHABET, EPSILON


# ── Internal helpers ─────────────────────────────────────

def _build_graph(states, id_fn, transitions_fn):
    """Build a networkx MultiDiGraph and collect edge labels."""
    G = nx.MultiDiGraph()
    for s in states:
        G.add_node(id_fn(s))

    edge_labels: dict[tuple, str] = {}
    for s in states:
        for sym, targets in transitions_fn(s).items():
            for t in (targets if isinstance(targets, (set, frozenset, list)) else [targets]):
                sid, tid = id_fn(s), id_fn(t)
                G.add_edge(sid, tid)
                k = (sid, tid)
                edge_labels[k] = (edge_labels.get(k, "") + sym + " ").strip()
    return G, edge_labels


def _node_color(node_id, start_id, accept_ids, active_ids=None):
    is_start  = node_id == start_id
    is_accept = node_id in accept_ids
    is_active = active_ids and node_id in active_ids
    if is_active:              return NODE_COLORS["active"]
    if is_start and is_accept: return NODE_COLORS["both"]
    if is_start:               return NODE_COLORS["start"]
    if is_accept:              return NODE_COLORS["accept"]
    return NODE_COLORS["normal"]


def _legend(ax, items):
    ax.legend(
        handles=[mpatches.Patch(color=c, label=l) for c, l in items],
        loc="upper left", fontsize=8.5, framealpha=0.9, edgecolor="#ccc",
    )


# ── Public drawing functions ─────────────────────────────

def draw_nfa(
    nfa: NFA,
    ax=None,
    active=None,
    pos: dict | None = None,
    title: str = "NFA",
) -> dict:
    """
    Draw the NFA on a matplotlib axis.

    Args:
        nfa:    the NFA to draw
        ax:     matplotlib Axes (created if None)
        active: set of NFAState currently active (highlighted red)
        pos:    pre-computed networkx layout — pass the returned dict on
                subsequent calls to keep the graph layout stable
        title:  axis title

    Returns:
        pos dict — store and pass back for stable layouts across re-draws.
    """
    states = sorted(nfa.all_states())
    G, edge_labels = _build_graph(states, id_fn=str,
                                   transitions_fn=lambda s: s.transitions)

    if pos is None:
        pos = nx.spring_layout(G, seed=42, k=2.2)

    active_ids = {str(s) for s in active} if active else set()

    if ax is None:
        _, ax = plt.subplots(figsize=(9, 6))
    ax.figure.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")

    colors = [_node_color(n, str(nfa.start), {str(nfa.accept)}, active_ids)
              for n in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=1000,
                           linewidths=1.5, edgecolors="#555", ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight="bold", ax=ax)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=20, edge_color="#445",
                           connectionstyle="arc3,rad=0.18",
                           min_source_margin=18, min_target_margin=18, ax=ax)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8.5,
                                  bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8),
                                  ax=ax)
    _legend(ax, [
        (NODE_COLORS["start"],  "Start state"),
        (NODE_COLORS["accept"], "Accept state"),
        (NODE_COLORS["active"], "Active state"),
        (NODE_COLORS["normal"], "Normal state"),
    ])
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10, color="#1a2f4a")
    ax.axis("off")
    return pos


def draw_dfa(
    start_dfa: DFAState,
    dfa_states: list[DFAState],
    ax=None,
    title: str = "DFA (Subset Construction)",
):
    """Draw the DFA produced by subset construction."""
    G, edge_labels = _build_graph(
        dfa_states,
        id_fn=lambda s: s.label(),
        transitions_fn=lambda s: {ch: [t] for ch, t in s.transitions.items()},
    )
    pos = nx.spring_layout(G, seed=7, k=3.0)
    accept_labels = {s.label() for s in dfa_states if s.is_accept}

    if ax is None:
        _, ax = plt.subplots(figsize=(9, 6))
    ax.figure.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")

    colors = [_node_color(n, start_dfa.label(), accept_labels) for n in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=1400,
                           linewidths=1.5, edgecolors="#555", ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=6.5, font_weight="bold", ax=ax)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=20, edge_color="#445",
                           connectionstyle="arc3,rad=0.2",
                           min_source_margin=22, min_target_margin=22, ax=ax)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8.5,
                                  bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8),
                                  ax=ax)
    _legend(ax, [
        (NODE_COLORS["start"],  "Start state"),
        (NODE_COLORS["accept"], "Accept state"),
        (NODE_COLORS["both"],   "Start + Accept"),
        (NODE_COLORS["normal"], "Normal state"),
    ])
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10, color="#1a2f4a")
    ax.axis("off")


def make_transition_table(nfa: NFA) -> pd.DataFrame:
    """Return a DataFrame showing the full NFA transition function δ."""
    states  = sorted(nfa.all_states())
    symbols = sorted(DNA_ALPHABET | {EPSILON})
    rows = []
    for s in states:
        row = {
            "State": str(s)
                     + (" ▶" if s == nfa.start else "")
                     + (" ✓" if s.is_accept    else "")
        }
        for sym in symbols:
            targets = s.transitions.get(sym, set())
            row[sym] = (
                "{" + ", ".join(str(t) for t in sorted(targets)) + "}"
                if targets else "∅"
            )
        rows.append(row)
    return pd.DataFrame(rows)