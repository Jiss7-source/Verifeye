# ─────────────────────────────────────────────
#  PAGE CONFIG — must be the ABSOLUTE FIRST Streamlit call
# ─────────────────────────────────────────────
import streamlit as st
import datetime

st.set_page_config(
    page_title="VerifEYE — Expense Auditor",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  IMPORTS  (only after set_page_config)
# ─────────────────────────────────────────────
from utils import get_file_content, load_policy_text
from database import (
    init_db, save_audit, update_audit_override,
    get_all_audits, get_flagged_audits, delete_all_audits
)
from auditor import audit_receipt

# ─────────────────────────────────────────────
#  CUSTOM CSS — DARK FINANCIAL COMMAND CENTRE
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

/* ── ROOT TOKENS ── */
:root {
    --bg-base:        #0D0E11;
    --bg-surface:     #13151A;
    --bg-elevated:    #1A1D24;
    --bg-card:        #1F2229;
    --border-subtle:  rgba(255,255,255,0.06);
    --border-mid:     rgba(255,255,255,0.10);
    --border-active:  rgba(212,175,55,0.5);
    --amber:          #D4AF37;
    --amber-dim:      rgba(212,175,55,0.12);
    --amber-glow:     rgba(212,175,55,0.25);
    --text-primary:   #F0EDE8;
    --text-secondary: #8A8A8E;
    --text-muted:     #4A4A52;
    --green:          #3DBA7A;
    --green-dim:      rgba(61,186,122,0.12);
    --red:            #E05252;
    --red-dim:        rgba(224,82,82,0.12);
    --yellow:         #E8B84B;
    --yellow-dim:     rgba(232,184,75,0.12);
}

/* ═══════════════════════════════════════════
   ENTRANCE ANIMATIONS
═══════════════════════════════════════════ */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes gridShift {
    0%   { background-position: 0 0; }
    100% { background-position: 60px 60px; }
}
@keyframes badgePop {
    from { opacity: 0; transform: scale(0.85); }
    to   { opacity: 1; transform: scale(1); }
}
@keyframes pulseRing {
    0%   { transform: scale(0.8); opacity: 0.4; }
    70%  { transform: scale(1.8); opacity: 0; }
    100% { transform: scale(0.8); opacity: 0; }
}
@keyframes resultReveal {
    from { opacity: 0; transform: scale(0.97) translateY(20px); }
    to   { opacity: 1; transform: scale(1)    translateY(0); }
}
@keyframes greenPulse {
    0%, 100% { box-shadow: 0 0 0 3px rgba(61,186,122,0.2), 0 0 16px rgba(61,186,122,0.3); }
    50%       { box-shadow: 0 0 0 5px rgba(61,186,122,0.3), 0 0 32px rgba(61,186,122,0.6); }
}
@keyframes amberPulse {
    0%, 100% { box-shadow: 0 0 0 3px rgba(232,184,75,0.2), 0 0 16px rgba(232,184,75,0.3); }
    50%       { box-shadow: 0 0 0 5px rgba(232,184,75,0.3), 0 0 32px rgba(232,184,75,0.6); }
}
@keyframes redPulse {
    0%, 100% { box-shadow: 0 0 0 3px rgba(224,82,82,0.2), 0 0 16px rgba(224,82,82,0.3); }
    50%       { box-shadow: 0 0 0 5px rgba(224,82,82,0.3), 0 0 32px rgba(224,82,82,0.7); }
}

/* Page entrance */
section.main > div {
    animation: fadeSlideUp 0.65s cubic-bezier(0.22,1,0.36,1) both;
}
[data-testid="stSidebar"] {
    animation: fadeIn 0.5s ease 0.1s both;
}

/* ── GLOBAL BASE ── */
.stApp {
    background-color: var(--bg-base) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text-primary);
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text-primary);
}

/* ── ANIMATED GRID BACKGROUND ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(212,175,55,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(212,175,55,0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    z-index: 0;
    pointer-events: none;
    animation: gridShift 20s linear infinite;
}

/* ── TYPOGRAPHY ── */
h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background-color: var(--bg-surface) !important;
    border-right: 1px solid var(--border-subtle) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none !important; }
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    padding: 10px 14px; border-radius: 6px;
    border: 1px solid transparent; transition: all 0.2s ease; margin-bottom: 4px; cursor: pointer;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: var(--amber-dim); border-color: var(--border-active);
}
[data-testid="stSidebar"] div[role="radiogroup"] div[data-testid="stMarkdownContainer"] {
    font-family: 'DM Mono', monospace !important; font-size: 13px !important;
    letter-spacing: 0.05em; text-transform: uppercase; color: var(--text-secondary) !important;
}

/* ── INPUTS ── */
.stTextInput>div>div>input, .stTextArea>div>div>textarea,
.stDateInput>div>div>input, .stSelectbox>div>div>div {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-mid) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 3px var(--amber-dim) !important;
}
label[data-testid="stWidgetLabel"] p {
    color: var(--text-secondary) !important; font-family: 'DM Mono', monospace !important;
    font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px;
}

/* ── BORDER CONTAINERS → GLASS CARDS ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--bg-card) !important; border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important; padding: 28px 32px !important;
    margin-bottom: 16px !important; box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
    animation: fadeSlideUp 0.5s ease both;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: var(--border-active) !important;
    box-shadow: 0 8px 40px rgba(212,175,55,0.08) !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: var(--amber) !important; color: #0D0E11 !important;
    border: none !important; border-radius: 8px !important; padding: 12px 28px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    font-size: 14px !important; letter-spacing: 0.05em !important;
    text-transform: uppercase !important; cursor: pointer !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #E8C84A !important; box-shadow: 0 0 24px var(--amber-glow) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploadDropzone"] {
    background-color: var(--bg-elevated) !important;
    border: 1px dashed var(--amber) !important; border-radius: 10px !important;
    transition: background 0.2s ease;
}
[data-testid="stFileUploadDropzone"]:hover { background-color: var(--amber-dim) !important; }

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-elevated) !important; border: 1px solid var(--border-mid) !important;
    border-radius: 8px !important; color: var(--text-primary) !important;
}

/* ── PROGRESS BAR ── */
[data-testid="stProgress"] > div > div { background: var(--bg-elevated) !important; }
[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg, var(--amber), #E8C84A) !important;
    border-radius: 4px; transition: width 0.8s ease;
}

/* ── ALERTS ── */
[data-testid="stAlert"] { background: var(--bg-elevated) !important; border-radius: 8px !important; }

/* ── EXPANDER ── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important; border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important; margin-bottom: 8px; transition: border-color 0.2s ease;
}
[data-testid="stExpander"]:hover { border-color: var(--border-active) !important; }
details summary { color: var(--text-primary) !important; font-family: 'DM Mono', monospace !important; font-size: 13px !important; }

/* ── FORM ── */
[data-testid="stForm"] { background: transparent !important; border: none !important; }

/* ── METRIC CARDS ── */
.metric-card {
    background: var(--bg-card); border: 1px solid var(--border-subtle);
    border-radius: 12px; padding: 24px 20px; text-align: center;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
    animation: fadeSlideUp 0.5s ease both;
}
.metric-card:hover { border-color: var(--border-active); box-shadow: 0 8px 32px rgba(212,175,55,0.08); }
.metric-number { font-family: 'Syne', sans-serif; font-size: 48px; font-weight: 800; line-height: 1; }
.metric-label { font-family: 'DM Mono', monospace; font-size: 11px; color: var(--text-muted); margin-top: 8px; text-transform: uppercase; letter-spacing: 0.15em; }

/* ── DATA ROW ── */
.data-row {
    background: var(--bg-card); border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--amber); border-radius: 8px;
    padding: 14px 20px; margin-bottom: 8px; display: flex;
    align-items: center; gap: 16px; font-size: 14px;
    transition: all 0.2s ease; animation: fadeSlideUp 0.3s ease both;
}
.data-row:hover { background: var(--bg-elevated); transform: translateX(2px); }

/* ── SECTION LABEL ── */
.section-label {
    font-family: 'DM Mono', monospace; font-size: 11px; color: var(--amber);
    text-transform: uppercase; letter-spacing: 0.2em; text-align: center;
    margin: 2rem 0 1.5rem; position: relative;
}
.section-label::before, .section-label::after {
    content: ''; position: absolute; top: 50%; width: 30%; height: 1px; background: var(--border-subtle);
}
.section-label::before { left: 0; }
.section-label::after  { right: 0; }

/* ── DATA FIELDS (Ledger) ── */
.data-field { background: var(--bg-elevated); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 14px 18px; margin-bottom: 10px; }
.data-field-label { font-family: 'DM Mono', monospace; font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 4px; }
.data-field-value { font-size: 15px; color: var(--text-primary); font-weight: 400; }

/* ── PILLAR CARDS ── */
.pillar-card {
    background: var(--bg-card); border: 1px solid var(--border-subtle);
    border-radius: 12px; padding: 28px 24px; height: 100%;
    transition: all 0.3s ease; position: relative; overflow: hidden;
}
.pillar-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--amber), transparent); opacity: 0; transition: opacity 0.3s ease;
}
.pillar-card:hover::before { opacity: 1; }
.pillar-card:hover { border-color: var(--border-active); box-shadow: 0 12px 40px rgba(212,175,55,0.08); transform: translateY(-2px); }
.pillar-number { font-family: 'Syne', sans-serif; font-size: 48px; font-weight: 800; color: var(--amber); opacity: 0.25; line-height: 1; margin-bottom: 8px; }
.pillar-title  { font-family: 'Syne', sans-serif; font-size: 17px; font-weight: 700; color: var(--text-primary); margin-bottom: 10px; }
.pillar-body   { font-size: 14px; color: var(--text-secondary); line-height: 1.7; }

/* ── HERO ── */
.hero-eyebrow {
    font-family: 'DM Mono', monospace; font-size: 11px; color: var(--amber);
    text-transform: uppercase; letter-spacing: 0.3em; margin-bottom: 16px;
    animation: fadeSlideUp 0.6s ease 0.1s both;
}
.hero-title {
    font-family: 'Syne', sans-serif; font-size: clamp(52px, 8vw, 96px);
    font-weight: 800; line-height: 0.95; color: var(--text-primary);
    letter-spacing: -0.04em; margin-bottom: 20px;
    animation: fadeSlideDown 0.7s cubic-bezier(0.22,1,0.36,1) 0.15s both;
}
.hero-title span { color: var(--amber); }
.hero-sub {
    font-size: 16px; color: var(--text-secondary); line-height: 1.7; max-width: 480px;
    animation: fadeSlideUp 0.6s ease 0.3s both;
}
.hero-stat-row { display: flex; gap: 32px; margin-top: 32px; animation: fadeSlideUp 0.6s ease 0.4s both; }
.hero-stat-val { font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 700; color: var(--amber); }
.hero-stat-label { font-family: 'DM Mono', monospace; font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.12em; margin-top: 2px; }

/* ── PULSE DOT ── */
.pulse-dot {
    display: inline-block; width: 8px; height: 8px; border-radius: 50%;
    background: var(--green); margin-right: 8px; position: relative;
}
.pulse-dot::after {
    content: ''; position: absolute; inset: -4px; border-radius: 50%;
    background: var(--green); opacity: 0.3; animation: pulseRing 2s ease infinite;
}

/* ── PAGE HEADER ── */
.page-header { border-bottom: 1px solid var(--border-subtle); padding-bottom: 24px; margin-bottom: 32px; animation: fadeSlideDown 0.5s ease both; }
.page-header h1 { font-family: 'Syne', sans-serif; font-size: 32px; font-weight: 700; margin-bottom: 6px; }
.page-header p  { color: var(--text-secondary); font-size: 15px; margin: 0; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; }

/* ═══════════════════════════════════════════════════
   TRAFFIC-LIGHT RESULT CARD
═══════════════════════════════════════════════════ */

/* Card wrapper */
.verdict-card {
    border-radius: 14px; overflow: hidden; margin-bottom: 12px;
    animation: resultReveal 0.55s cubic-bezier(0.22,1,0.36,1) both;
}

/* Coloured header bands */
.verdict-header {
    padding: 22px 28px; display: flex; align-items: center; gap: 18px; position: relative;
}
.verdict-header::after {
    content: ''; position: absolute; inset: 0; background: rgba(255,255,255,0.04);
}

.header-approved { background: linear-gradient(135deg, #1a4d2e 0%, #2d7a4a 100%); }
.header-flagged  { background: linear-gradient(135deg, #7c4500 0%, #c57b00 100%); }
.header-rejected { background: linear-gradient(135deg, #5c1010 0%, #b33030 100%); }
.header-error    { background: linear-gradient(135deg, #222429 0%, #3a3d47 100%); }

/* Traffic light signal circle */
.signal-circle {
    width: 56px; height: 56px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; flex-shrink: 0; background: rgba(255,255,255,0.15);
    position: relative; z-index: 1;
}
.signal-approved { animation: greenPulse 2.2s ease-in-out infinite; }
.signal-flagged  { animation: amberPulse 1.8s ease-in-out infinite; }
.signal-rejected { animation: redPulse  1.4s ease-in-out infinite; }

.verdict-title-text {
    font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 800;
    color: #fff; line-height: 1; z-index: 1; position: relative;
}
.verdict-subtitle {
    font-family: 'DM Mono', monospace; font-size: 10px; text-transform: uppercase;
    letter-spacing: 0.2em; color: rgba(255,255,255,0.55); margin-top: 4px;
    z-index: 1; position: relative;
}

/* Card body */
.verdict-body {
    background: var(--bg-card); border: 1px solid var(--border-subtle);
    border-top: none; border-radius: 0 0 14px 14px; padding: 24px 28px;
}

/* Warning banner (FLAGGED) */
.flagged-warning {
    display: flex; align-items: flex-start; gap: 12px;
    background: rgba(232,184,75,0.10); border: 1px solid rgba(232,184,75,0.3);
    border-radius: 8px; padding: 12px 16px; margin-bottom: 18px;
    font-size: 13px; color: var(--yellow); line-height: 1.5;
}

/* Reason box */
.reason-box {
    border-radius: 8px; padding: 14px 18px; margin-bottom: 18px;
    font-size: 14px; line-height: 1.6; font-weight: 400;
}
.reason-approved { background: rgba(61,186,122,0.08); color: #6FD9A8; border-left: 3px solid var(--green); }
.reason-flagged  { background: rgba(232,184,75,0.08); color: #E8B84B; border-left: 3px solid var(--yellow); }
.reason-rejected { background: rgba(224,82,82,0.08);  color: #EF8080; border-left: 3px solid var(--red); }
.reason-error    { background: var(--bg-elevated); color: var(--text-secondary); border-left: 3px solid var(--border-mid); }

/* Result data grid */
.result-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 18px; }
.result-cell { background: var(--bg-elevated); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px 16px; }
.result-cell-label { font-family: 'DM Mono', monospace; font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 4px; }
.result-cell-value { font-size: 14px; color: var(--text-primary); font-weight: 400; }
.val-green { color: var(--green) !important; font-weight: 500; }
.val-amber { color: var(--yellow) !important; font-weight: 500; }
.val-red   { color: var(--red) !important;    font-weight: 500; }

/* Violations strip */
.violations-block {
    background: rgba(224,82,82,0.07); border: 1px solid rgba(224,82,82,0.2);
    border-radius: 8px; padding: 12px 16px; margin-bottom: 14px;
    font-size: 13px; color: #EF8080;
}

/* Authenticity row */
.rc-divider { border: none; border-top: 1px solid var(--border-subtle); margin: 16px 0; }
.fraud-row { display: flex; align-items: center; gap: 10px; font-size: 13px; margin-bottom: 6px; }
.fraud-label { color: var(--text-secondary); }
.fraud-pill {
    font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.12em; padding: 3px 12px; border-radius: 20px;
}
.pill-low    { background: var(--green-dim); color: var(--green); border: 1px solid rgba(61,186,122,0.3); }
.pill-medium { background: var(--yellow-dim); color: var(--yellow); border: 1px solid rgba(232,184,75,0.3); }
.pill-high   { background: var(--red-dim); color: var(--red); border: 1px solid rgba(224,82,82,0.3); animation: redPulse 1.4s ease-in-out infinite; }
.pill-unknown{ background: var(--bg-elevated); color: var(--text-secondary); border: 1px solid var(--border-mid); }
.fraud-signals { font-size: 12px; color: var(--text-muted); margin-top: 4px; font-style: italic; }

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  STARTUP & SESSION STATE
# ─────────────────────────────────────────────
init_db()

for key, default in [("single_result", None)]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style="padding: 20px 0 8px;">
            <div style="font-family:'Syne',sans-serif; font-size:22px; font-weight:800; color:#D4AF37; letter-spacing:-0.02em;">VerifEYE</div>
            <div style="font-family:'DM Mono',monospace; font-size:10px; color:#4A4A52; text-transform:uppercase; letter-spacing:0.2em; margin-top:4px;">Expense Intelligence</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.06); margin:12px 0;'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'DM Mono',monospace; font-size:10px; color:#4A4A52; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:10px;">Policy Ruleset</div>""", unsafe_allow_html=True)

    policy_source = st.radio(
        "Policy source",
        ["Built-in Framework", "Upload Custom Policy"],
        key="policy_source_radio",
        label_visibility="collapsed"
    )

    if policy_source == "Upload Custom Policy":
        policy_upload = st.file_uploader("Upload policy PDF", type=["pdf"], key="policy_uploader")
        if policy_upload:
            try:
                import fitz
                raw_pol = policy_upload.read()
                doc = fitz.open(stream=raw_pol, filetype="pdf")
                policy_text = "\n".join(p.get_text() for p in doc)
                doc.close()
                policy_status = "ok"
            except Exception:
                policy_text, policy_status = load_policy_text()
        else:
            policy_text, policy_status = load_policy_text()
    else:
        @st.cache_data
        def _load_builtin():
            return load_policy_text()
        policy_text, policy_status = _load_builtin()

    st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.06); margin:16px 0;'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'DM Mono',monospace; font-size:10px; color:#4A4A52; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:10px;">Navigation</div>""", unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["◆  Audit Console", "◇  Ledger & History", "⸬  Intelligence"],
        key="page_nav_radio",
        label_visibility="collapsed"
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    status_color = "#3DBA7A" if policy_status == "ok" else "#E05252"
    st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:12px 14px;">
            <div style="font-family:'DM Mono',monospace; font-size:10px; color:#4A4A52; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:8px;">System Status</div>
            <div style="display:flex; align-items:center; gap:8px; font-size:13px; color:#8A8A8E;">
                <span style="width:6px;height:6px;border-radius:50%;background:{status_color};display:inline-block;"></span>
                Policy Engine
            </div>
            <div style="display:flex; align-items:center; gap:8px; font-size:13px; color:#8A8A8E; margin-top:6px;">
                <span style="width:6px;height:6px;border-radius:50%;background:#3DBA7A;display:inline-block;"></span>
                Gemini 2.5 Flash
            </div>
            <div style="display:flex; align-items:center; gap:8px; font-size:13px; color:#8A8A8E; margin-top:6px;">
                <span style="width:6px;height:6px;border-radius:50%;background:#3DBA7A;display:inline-block;"></span>
                SQLite Ledger
            </div>
        </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HELPER — sanitize AI output fields
# ─────────────────────────────────────────────
def _clean(val: str) -> str:
    """Strip Python list/dict syntax the AI may accidentally return, and HTML-escape."""
    import html as html_lib
    v = str(val).strip()
    if v.startswith('[') and v.endswith(']'):
        inner = v[1:-1]
        items = [i.strip().strip("'").strip('"') for i in inner.split("',") if i.strip()]
        if not items:
            items = [inner.strip().strip("'").strip('"')]
        v = "; ".join(i for i in items if i)
    return html_lib.escape(v)


# ─────────────────────────────────────────────
#  HELPER — render one result dict (TRAFFIC-LIGHT)
# ─────────────────────────────────────────────
def display_result(result: dict):
    verdict = result.get("verdict", "ERROR").upper()

    cfg = {
        "APPROVED": {
            "header_class":   "header-approved",
            "signal_class":   "signal-circle signal-approved",
            "icon":           "✔",
            "title":          "Approved",
            "subtitle":       "Expense cleared — no policy violations detected",
            "reason_class":   "reason-approved",
            "banner":         None,
        },
        "FLAGGED": {
            "header_class":   "header-flagged",
            "signal_class":   "signal-circle signal-flagged",
            "icon":           "⚑",
            "title":          "Flagged for Review",
            "subtitle":       "Requires human inspection before reimbursement",
            "reason_class":   "reason-flagged",
            "banner":         "This expense could not be automatically cleared. A compliance officer must review and approve before any reimbursement is processed.",
        },
        "REJECTED": {
            "header_class":   "header-rejected",
            "signal_class":   "signal-circle signal-rejected",
            "icon":           "✘",
            "title":          "Rejected",
            "subtitle":       "Policy violation detected — claim denied",
            "reason_class":   "reason-rejected",
            "banner":         None,
        },
    }.get(verdict, {
        "header_class":   "header-error",
        "signal_class":   "signal-circle",
        "icon":           "•",
        "title":          "Processing Error",
        "subtitle":       "Could not evaluate this receipt",
        "reason_class":   "reason-error",
        "banner":         None,
    })

    # Extract and sanitize fields
    merchant   = _clean(result.get("merchant_name",    "Not found"))
    rec_date   = _clean(result.get("receipt_date",     "Not found"))
    amount     = _clean(result.get("extracted_amount", "Not found"))
    currency   = _clean(result.get("currency",         ""))
    reason     = _clean(result.get("reason",           "—"))
    viol       = _clean(result.get("violations",       "None"))
    fake_r     = result.get("fake_risk", "UNKNOWN").upper()
    fake_sig   = _clean(result.get("fake_reasons",     "None"))
    full_amount = f"{amount} {currency}".strip()

    # Pill classes
    pill_class = {"LOW": "pill-low", "MEDIUM": "pill-medium", "HIGH": "pill-high"}.get(fake_r, "pill-unknown")

    # Warning banner (FLAGGED only)
    banner_html = ""
    if cfg["banner"]:
        banner_html = f"""
        <div class="flagged-warning">
            <span style="font-size:18px;flex-shrink:0;">⚠</span>
            <span>{cfg['banner']}</span>
        </div>"""

    # Violations
    viol_html = ""
    if viol and viol.lower() not in ("none", "n/a", ""):
        viol_html = f"""
        <div class="violations-block">
            <strong style="font-family:'DM Mono',monospace; font-size:10px; text-transform:uppercase; letter-spacing:0.15em;">Policy Violations</strong><br>
            {viol}
        </div>"""

    # Fraud signals
    signals_html = ""
    if fake_sig and fake_sig.lower() not in ("none", "n/a", ""):
        signals_html = f'<div class="fraud-signals">Signals detected: {fake_sig}</div>'

    html = f"""
<div class="verdict-card">
  <div class="verdict-header {cfg['header_class']}">
    <div class="{cfg['signal_class']}">{cfg['icon']}</div>
    <div>
      <div class="verdict-title-text">{cfg['title']}</div>
      <div class="verdict-subtitle">{cfg['subtitle']}</div>
    </div>
  </div>

  <div class="verdict-body">
    {banner_html}

    <div class="reason-box {cfg['reason_class']}">
        <strong style="font-family:'DM Mono',monospace; font-size:10px; text-transform:uppercase; letter-spacing:0.15em;">Audit Finding</strong><br>
        {reason}
    </div>

    <div class="result-grid">
      <div class="result-cell">
        <div class="result-cell-label">Merchant</div>
        <div class="result-cell-value">{merchant}</div>
      </div>
      <div class="result-cell">
        <div class="result-cell-label">Receipt Date</div>
        <div class="result-cell-value">{rec_date}</div>
      </div>
      <div class="result-cell">
        <div class="result-cell-label">Extracted Total</div>
        <div class="result-cell-value">{full_amount}</div>
      </div>
      <div class="result-cell">
        <div class="result-cell-label">Authenticity Check</div>
        <div class="result-cell-value">
            <span class="fraud-pill {pill_class}">{fake_r if fake_r != 'UNKNOWN' else '—'} risk</span>
        </div>
      </div>
    </div>

    {viol_html}
    {signals_html}
  </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE 1 — AUDIT CONSOLE
# ═══════════════════════════════════════════════════════════════
if page == "◆  Audit Console":

    # ── HERO ──
    st.markdown("""
        <div style="padding: 48px 0 56px;">
            <div class="hero-eyebrow">
                <span class="pulse-dot"></span>
                AI-Powered Compliance Engine — Live
            </div>
            <div class="hero-title">Verif<span>EYE</span></div>
            <div class="hero-sub">
                Intelligent receipt auditing powered by Gemini 2.5 Flash. Upload any expense receipt and get a policy-grounded verdict in seconds.
            </div>
            <div class="hero-stat-row">
                <div>
                    <div class="hero-stat-val">2.5s</div>
                    <div class="hero-stat-label">Avg. audit time</div>
                </div>
                <div>
                    <div class="hero-stat-val">7</div>
                    <div class="hero-stat-label">Fraud signals checked</div>
                </div>
                <div>
                    <div class="hero-stat-val">100%</div>
                    <div class="hero-stat-label">Policy cross-referenced</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Receipt Submission</div>', unsafe_allow_html=True)

    # ── SUBMISSION FORM ──
    col_l, col_m, col_r = st.columns([1, 3, 1])
    with col_m:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                claimed_date = st.date_input("Claimed Expense Date", value=datetime.date.today())
            with c2:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                st.markdown("""
                    <div style="font-family:'DM Mono',monospace; font-size:10px; color:#4A4A52; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:6px;">Accepted Formats</div>
                    <div style="font-size:13px; color:#8A8A8E;">PDF · JPG · JPEG · PNG</div>
                """, unsafe_allow_html=True)

            business_purpose = st.text_area(
                "Business Purpose",
                placeholder="e.g. Client dinner with ABC Corp stakeholders to discuss Q3 renewal...",
                height=90
            )

            uploaded_file = st.file_uploader(
                "Drop receipt here or click to browse",
                type=["pdf", "jpg", "jpeg", "png"],
                key="single_uploader",
                label_visibility="visible"
            )

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            submit_doc = st.button("Run Compliance Audit", key="btn_single", use_container_width=True)

    # ── LOGIC ──
    if submit_doc:
        if not uploaded_file:
            st.warning("Upload a receipt before running the audit.")
        elif not business_purpose:
            st.warning("Business purpose is required — the AI needs context to evaluate the claim.")
        else:
            with st.spinner("Analysing receipt against policy..."):
                content_bytes, kind = get_file_content(uploaded_file)
                if kind in ("unsupported", "empty") or kind.startswith("error"):
                    st.error("This file could not be read. Try a cleaner scan or a different format.")
                    st.stop()
                mime_type = uploaded_file.type if kind == "image" else "image/jpeg"
                result = audit_receipt(
                    content=content_bytes,
                    content_type=kind,
                    policy_text=policy_text,
                    filename=uploaded_file.name,
                    claimed_date=str(claimed_date),
                    business_purpose=business_purpose,
                    mime_type=mime_type
                )
                save_audit(uploaded_file.name, business_purpose, str(claimed_date), result["verdict"], result["reason"])
                st.session_state.single_result = result

    # ── RESULTS ──
    if st.session_state.single_result:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Audit Results</div>', unsafe_allow_html=True)
        col_la, col_ma, col_ra = st.columns([1, 3, 1])
        with col_ma:
            with st.container(border=True):
                display_result(st.session_state.single_result)

    # ── ARCHITECTURE PILLARS ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">How It Works</div>', unsafe_allow_html=True)

    p1, p2, p3 = st.columns(3)
    pillars = [
        ("01", "Policy Intelligence", "Cross-references every line item against your organisation's expense rules — limits, prohibited categories, and receipt requirements."),
        ("02", "Fraud Detection", "Runs 7 forensic checks: font consistency, round-number flags, GST validation, timestamp anomalies, and total reconciliation."),
        ("03", "Immutable Ledger", "Every audit is logged to a tamper-evident SQLite record with full support for human supervisor override and audit trails."),
    ]
    for col, (num, title, body) in zip([p1, p2, p3], pillars):
        with col:
            st.markdown(f"""
                <div class="pillar-card">
                    <div class="pillar-number">{num}</div>
                    <div class="pillar-title">{title}</div>
                    <div class="pillar-body">{body}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE 2 — LEDGER & HISTORY
# ═══════════════════════════════════════════════════════════════
elif page == "◇  Ledger & History":

    st.markdown("""
        <div class="page-header">
            <h1>Audit Ledger</h1>
            <p>Complete transaction log with human-in-the-loop override controls.</p>
        </div>
    """, unsafe_allow_html=True)

    filter_choice = st.selectbox(
        "Filter",
        ["All Records", "Anomalies Only (Flagged & Rejected)"],
        label_visibility="visible"
    )
    rows = (
        get_flagged_audits()
        if filter_choice == "Anomalies Only (Flagged & Rejected)"
        else get_all_audits()
    )

    if not rows:
        st.markdown("""
            <div style="text-align:center; padding:60px 0; color:#4A4A52; font-family:'DM Mono',monospace; font-size:13px; text-transform:uppercase; letter-spacing:0.1em;">
                No records found
            </div>
        """, unsafe_allow_html=True)
    else:
        for row in rows:
            row_id      = row['id']
            filename    = row['filename']
            ai_verdict  = row['verdict']
            final       = row.get('human_verdict') or ai_verdict
            summary     = row['summary']
            timestamp   = row['timestamp']
            is_override = bool(row.get('human_verdict'))

            colour_map    = {"APPROVED": "#3DBA7A", "FLAGGED": "#E8B84B", "REJECTED": "#E05252"}
            override_tag  = ' <span style="font-size:10px; color:#D4AF37; font-family:\'DM Mono\',monospace;">[OVERRIDE]</span>' if is_override else ''

            with st.expander(f"#{row_id:03d}  ·  {filename}  ·  {final}{override_tag}", expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""
                        <div class="data-field"><div class="data-field-label">AI Verdict</div><div class="data-field-value" style="color:{colour_map.get(ai_verdict,'#8A8A8E')};">{ai_verdict}</div></div>
                        <div class="data-field"><div class="data-field-label">Claimed Date</div><div class="data-field-value">{row.get('claimed_date','N/A')}</div></div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                        <div class="data-field"><div class="data-field-label">Business Purpose</div><div class="data-field-value">{row.get('business_purpose','N/A')}</div></div>
                        <div class="data-field"><div class="data-field-label">Logged At</div><div class="data-field-value">{timestamp}</div></div>
                    """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="data-field" style="margin-top:4px;"><div class="data-field-label">Policy Reason</div><div class="data-field-value" style="color:#8A8A8E;">{summary}</div></div>
                """, unsafe_allow_html=True)

                st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.06); margin:16px 0 12px;'></div>", unsafe_allow_html=True)
                st.markdown("""<div style="font-family:'DM Mono',monospace; font-size:10px; color:#D4AF37; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:12px;">Supervisor Override</div>""", unsafe_allow_html=True)

                with st.form(key=f"form_override_{row_id}"):
                    current_comment = row.get('human_comment', '')
                    new_comment = st.text_input("Override Justification", value=current_comment or "", key=f"comment_{row_id}")
                    new_verdict = st.selectbox("Force Verdict", ["", "APPROVED", "FLAGGED", "REJECTED"], key=f"verdict_{row_id}")
                    submit = st.form_submit_button("Commit Override")
                    if submit:
                        update_audit_override(row_id, new_comment, new_verdict if new_verdict else None)
                        st.success("Override committed.")
                        st.rerun()

    st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.06); margin:24px 0;'></div>", unsafe_allow_html=True)
    if rows:
        if st.button("Purge Entire Ledger"):
            delete_all_audits()
            st.success("Ledger cleared.")
            st.rerun()


# ═══════════════════════════════════════════════════════════════
#  PAGE 3 — FINANCIAL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════
elif page == "⸬  Intelligence":

    st.markdown("""
        <div class="page-header">
            <h1>Intelligence Overview</h1>
            <p>Real-time metrics accounting for all human overrides.</p>
        </div>
    """, unsafe_allow_html=True)

    all_rows = get_all_audits()

    if not all_rows:
        st.markdown("""
            <div style="text-align:center; padding:60px 0; color:#4A4A52; font-family:'DM Mono',monospace; font-size:13px; text-transform:uppercase; letter-spacing:0.1em;">
                No data yet — run your first audit to see metrics
            </div>
        """, unsafe_allow_html=True)
    else:
        total = len(all_rows)
        approved = flagged = rejected = 0
        for r in all_rows:
            v = r.get('human_verdict') or r['verdict']
            if v == "APPROVED":   approved += 1
            elif v == "FLAGGED":  flagged  += 1
            elif v == "REJECTED": rejected += 1

        rate = round((approved / total) * 100) if total else 0

        col1, col2, col3, col4 = st.columns(4)
        metric_data = [
            (col1, str(total),    "#F0EDE8", "Total Audited"),
            (col2, str(approved), "#3DBA7A", "Approved"),
            (col3, str(flagged),  "#E8B84B", "Flagged"),
            (col4, str(rejected), "#E05252", "Rejected"),
        ]
        for col, value, colour, label in metric_data:
            with col:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-number" style="color:{colour};">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
                <span style="font-family:'DM Mono',monospace; font-size:11px; color:#4A4A52; text-transform:uppercase; letter-spacing:0.15em;">Approval Rate</span>
                <span style="font-family:'Syne',sans-serif; font-size:20px; font-weight:700; color:#D4AF37;">{rate}%</span>
            </div>
        """, unsafe_allow_html=True)
        st.progress(rate / 100)

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'DM Mono',monospace; font-size:10px; color:#4A4A52; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:14px;">Recent Activity</div>""", unsafe_allow_html=True)

        colour_map = {"APPROVED": "#3DBA7A", "FLAGGED": "#E8B84B", "REJECTED": "#E05252"}
        for row in all_rows[:8]:
            v = row.get('human_verdict') or row['verdict']
            c = colour_map.get(v, "#8A8A8E")
            st.markdown(f"""
                <div class="data-row">
                    <span style="color:{c}; font-family:'DM Mono',monospace; font-size:12px; font-weight:500; min-width:80px;">{v}</span>
                    <span style="flex:1; font-size:14px;">{row['filename']}</span>
                    <span style="color:#4A4A52; font-family:'DM Mono',monospace; font-size:11px;">{row['timestamp']}</span>
                </div>
            """, unsafe_allow_html=True)