"""
DNA sequence rendering — produces styled HTML nucleotide boxes.

Color conventions follow common bioinformatics tools:
  A → red     C → blue     G → green     T → orange
"""

# Per-nucleotide background colors
NUC_COLORS: dict[str, str] = {
    "A": "#C0392B",
    "C": "#2980B9",
    "G": "#27AE60",
    "T": "#E67E22",
}

# NFA/DFA node colors for graph diagrams
NODE_COLORS: dict[str, str] = {
    "start":  "#6BCB77",   # green  — start state
    "accept": "#4D96FF",   # blue   — accept state
    "active": "#FF6B6B",   # red    — currently active (step-by-step)
    "both":   "#FFD166",   # gold   — start AND accept
    "normal": "#DDE6ED",   # grey   — plain state
}


def nuc_html(
    sequence: str,
    highlight: set[int] | None = None,
    active_idx: int | None = None,
) -> str:
    """
    Render a DNA sequence as a row of colored HTML nucleotide boxes.

    Args:
        sequence:   DNA string (A/C/G/T characters)
        highlight:  set of indices to mark as matched  (yellow outline)
        active_idx: single index being read this step  (red outline)

    Returns:
        HTML string — inject via st.markdown(..., unsafe_allow_html=True)
    """
    parts = ['<div class="seq-wrap">']
    for i, ch in enumerate(sequence):
        classes = f"nuc nuc-{ch}"
        if highlight and i in highlight:
            classes += " nuc-match"
        if active_idx is not None and i == active_idx:
            classes += " nuc-active"
        parts.append(
            f'<div class="{classes}">{ch}'
            f'<span class="idx">{i}</span></div>'
        )
    parts.append("</div>")
    return "".join(parts)