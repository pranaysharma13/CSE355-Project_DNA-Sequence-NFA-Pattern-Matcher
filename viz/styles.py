"""
Global CSS for the Streamlit app.
Kept in its own file so app.py stays focused on layout and logic.
Inject with: st.markdown(CSS, unsafe_allow_html=True)
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=DM+Sans:wght@400;500;700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* ── Page header ─────────────────────────────── */
.dna-header {
    background: linear-gradient(135deg, #0f1b2d 0%, #1a2f4a 60%, #0d2137 100%);
    border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
    border: 1px solid #1e3a5a;
}
.dna-title {
    font-size: 2.1rem; font-weight: 700; color: #E8F4FD;
    margin: 0; letter-spacing: -0.5px;
}
.dna-subtitle {
    font-size: 0.95rem; color: #7EB8D8; margin: 0.25rem 0 0 0;
    font-family: 'IBM Plex Mono', monospace;
}

/* ── DNA sequence boxes ───────────────────────── */
.seq-wrap {
    display: flex; flex-wrap: wrap; gap: 5px;
    margin: 1rem 0; align-items: flex-end;
}
.nuc {
    display: inline-flex; flex-direction: column; align-items: center;
    width: 34px; border-radius: 6px; padding: 4px 0;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700; font-size: 15px;
    color: white; user-select: none;
}
.nuc span.idx {
    font-size: 9px; font-weight: 400; opacity: 0.75; margin-top: 2px;
    font-family: 'IBM Plex Mono', monospace;
}
.nuc-A { background: #C0392B; }
.nuc-C { background: #2980B9; }
.nuc-G { background: #27AE60; }
.nuc-T { background: #E67E22; }
.nuc-match  {
    outline: 3px solid #F1C40F; outline-offset: 2px;
    transform: scale(1.08); z-index: 1; position: relative;
}
.nuc-active {
    outline: 3px solid #E74C3C; outline-offset: 2px;
    transform: scale(1.08); z-index: 1; position: relative;
}

/* ── Theory / info boxes ──────────────────────── */
.theory-box {
    background: #F0F7FF; border-left: 5px solid #2980B9;
    padding: 1rem 1.25rem; border-radius: 0 10px 10px 0;
    margin: 1rem 0; font-size: 0.92rem; line-height: 1.6;
}
.theory-box h4 { margin: 0 0 0.5rem 0; color: #1a5276; font-size: 1rem; }

/* ── Match result cards ───────────────────────── */
.match-card {
    background: #EAFAF1; border: 1.5px solid #27AE60;
    border-radius: 10px; padding: 0.75rem 1rem; margin: 0.5rem 0;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem;
}
.no-match-card {
    background: #FDFEFE; border: 1.5px dashed #BDC3C7;
    border-radius: 10px; padding: 0.75rem 1rem;
    color: #7F8C8D; font-size: 0.9rem;
}

/* ── Step-by-step badges ──────────────────────── */
.step-badge {
    display: inline-block; background: #1a2f4a; color: #7EB8D8;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem;
    padding: 0.3rem 0.75rem; border-radius: 20px; margin-bottom: 0.75rem;
}
.accept-badge {
    background: #1E8449; color: white; font-weight: 700;
    padding: 0.4rem 1rem; border-radius: 20px; display: inline-block;
}
.reject-badge {
    background: #922B21; color: white; font-weight: 700;
    padding: 0.4rem 1rem; border-radius: 20px; display: inline-block;
}

section[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
</style>
"""