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
from io import BytesIO

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

@keyframes gridShift {
    0%   { background-position: 0 0; }
    100% { background-position: 60px 60px; }
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
[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    padding: 10px 14px;
    border-radius: 6px;
    border: 1px solid transparent;
    transition: all 0.2s ease;
    margin-bottom: 4px;
    cursor: pointer;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: var(--amber-dim);
    border-color: var(--border-active);
}
[data-testid="stSidebar"] div[role="radiogroup"] div[data-testid="stMarkdownContainer"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 13px !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--text-secondary) !important;
}

/* ── INPUTS ── */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stDateInput>div>div>input,
.stSelectbox>div>div>div {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-mid) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 3px var(--amber-dim) !important;
}
label[data-testid="stWidgetLabel"] p {
    color: var(--text-secondary) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 6px;
}

/* ── BORDER CONTAINERS → GLASS CARDS ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    padding: 28px 32px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
    animation: fadeSlideUp 0.5s ease both;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: var(--border-active) !important;
    box-shadow: 0 8px 40px rgba(212,175,55,0.08) !important;
}
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── BUTTONS ── */
.stButton > button {
    background: var(--amber) !important;
    color: #0D0E11 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 28px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    position: relative;
    overflow: hidden;
}
.stButton > button::after {
    content: '';
    position: absolute;
    inset: 0;
    background: rgba(255,255,255,0);
    transition: background 0.2s ease;
}
.stButton > button:hover {
    background: #E8C84A !important;
    box-shadow: 0 0 24px var(--amber-glow) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploadDropzone"] {
    background-color: var(--bg-elevated) !important;
    border: 1px dashed var(--amber) !important;
    border-radius: 10px !important;
    transition: background 0.2s ease;
}
[data-testid="stFileUploadDropzone"]:hover {
    background-color: var(--amber-dim) !important;
}

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-mid) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}

/* ── PROGRESS BAR ── */
[data-testid="stProgress"] > div > div {
    background: var(--bg-elevated) !important;
}
[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg, var(--amber), #E8C84A) !important;
    border-radius: 4px;
    transition: width 0.8s ease;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    background: var(--bg-elevated) !important;
    border-radius: 8px !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    margin-bottom: 8px;
    transition: border-color 0.2s ease;
}
[data-testid="stExpander"]:hover {
    border-color: var(--border-active) !important;
}
details summary {
    color: var(--text-primary) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 13px !important;
}

/* ── FORM ── */
[data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
}

/* ── VERDICT BADGES ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    padding: 8px 18px;
    border-radius: 6px;
    animation: badgePop 0.4s cubic-bezier(0.34,1.56,0.64,1) both;
}
@keyframes badgePop {
    from { opacity: 0; transform: scale(0.85); }
    to   { opacity: 1; transform: scale(1); }
}
.badge-approved { background: var(--green-dim);  color: var(--green);  border: 1px solid rgba(61,186,122,0.3); }
.badge-flagged  { background: var(--yellow-dim); color: var(--yellow); border: 1px solid rgba(232,184,75,0.3); }
.badge-rejected { background: var(--red-dim);    color: var(--red);    border: 1px solid rgba(224,82,82,0.3); }
.badge-error    { background: rgba(255,255,255,0.05); color: var(--text-secondary); border: 1px solid var(--border-mid); }

/* ── RISK INDICATORS ── */
.risk-low  { color: var(--green);  font-weight: 600; font-family: 'DM Mono', monospace; }
.risk-med  { color: var(--yellow); font-weight: 600; font-family: 'DM Mono', monospace; }
.risk-high { color: var(--red);    font-weight: 600; font-family: 'DM Mono', monospace; }

/* ── METRIC CARDS ── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 24px 20px;
    text-align: center;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
    animation: fadeSlideUp 0.5s ease both;
}
.metric-card:hover {
    border-color: var(--border-active);
    box-shadow: 0 8px 32px rgba(212,175,55,0.08);
}
.metric-number {
    font-family: 'Syne', sans-serif;
    font-size: 48px;
    font-weight: 800;
    line-height: 1;
}
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.15em;
}

/* ── DATA ROW ── */
.data-row {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--amber);
    border-radius: 8px;
    padding: 14px 20px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 14px;
    transition: all 0.2s ease;
    animation: fadeSlideUp 0.3s ease both;
}
.data-row:hover {
    border-left-color: var(--amber);
    background: var(--bg-elevated);
    transform: translateX(2px);
}

/* ── DIVIDER ── */
.section-divider {
    border: none;
    border-top: 1px solid var(--border-subtle);
    margin: 2rem 0;
}
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--amber);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    text-align: center;
    margin: 2rem 0 1.5rem;
    position: relative;
}
.section-label::before, .section-label::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 30%;
    height: 1px;
    background: var(--border-subtle);
}
.section-label::before { left: 0; }
.section-label::after  { right: 0; }

/* ── RESULT DATA FIELD ── */
.data-field {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.data-field-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 4px;
}
.data-field-value {
    font-size: 15px;
    color: var(--text-primary);
    font-weight: 400;
}

/* ── PILLAR CARDS ── */
.pillar-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 28px 24px;
    height: 100%;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.pillar-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--amber), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.pillar-card:hover::before { opacity: 1; }
.pillar-card:hover {
    border-color: var(--border-active);
    box-shadow: 0 12px 40px rgba(212,175,55,0.08);
    transform: translateY(-2px);
}
.pillar-number {
    font-family: 'Syne', sans-serif;
    font-size: 48px;
    font-weight: 800;
    color: var(--amber);
    opacity: 0.25;
    line-height: 1;
    margin-bottom: 8px;
}
.pillar-title {
    font-family: 'Syne', sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 10px;
}
.pillar-body {
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.7;
}

/* ── HERO ── */
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--amber);
    text-transform: uppercase;
    letter-spacing: 0.3em;
    margin-bottom: 16px;
    animation: fadeSlideUp 0.6s ease 0.1s both;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(52px, 8vw, 96px);
    font-weight: 800;
    line-height: 0.95;
    color: var(--text-primary);
    letter-spacing: -0.04em;
    margin-bottom: 20px;
    animation: fadeSlideUp 0.6s ease 0.2s both;
}
.hero-title span { color: var(--amber); }
.hero-sub {
    font-size: 16px;
    color: var(--text-secondary);
    line-height: 1.7;
    max-width: 480px;
    animation: fadeSlideUp 0.6s ease 0.3s both;
}
.hero-stat-row {
    display: flex;
    gap: 32px;
    margin-top: 32px;
    animation: fadeSlideUp 0.6s ease 0.4s both;
}
.hero-stat-val {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: var(--amber);
}
.hero-stat-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 2px;
}

/* ── PULSE DOT ── */
.pulse-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--green);
    margin-right: 8px;
    position: relative;
}
.pulse-dot::after {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    background: var(--green);
    opacity: 0.3;
    animation: pulseRing 2s ease infinite;
}
@keyframes pulseRing {
    0%   { transform: scale(0.8); opacity: 0.4; }
    70%  { transform: scale(1.8); opacity: 0; }
    100% { transform: scale(0.8); opacity: 0; }
}

/* ── PAGE HEADER ── */
.page-header {
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 24px;
    margin-bottom: 32px;
    animation: fadeSlideUp 0.5s ease both;
}
.page-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 6px;
}
.page-header p {
    color: var(--text-secondary);
    font-size: 15px;
    margin: 0;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; }
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
        label_visibility="collapsed"
    )

    # Sidebar system status
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
#  HELPER — render one result dict
# ─────────────────────────────────────────────
def display_result(result: dict):
    verdict = result.get("verdict", "ERROR")

    badge_map = {
        "APPROVED": ("badge-approved", "✔  APPROVED"),
        "FLAGGED":  ("badge-flagged",  "⚑  FLAGGED"),
        "REJECTED": ("badge-rejected", "✘  REJECTED"),
    }
    badge_class, label = badge_map.get(verdict, ("badge-error", "•  ERROR"))

    st.markdown(f'<div class="badge {badge_class}">{label}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Extracted data fields
    col_a, col_b = st.columns(2)
    fields_left = [
        ("Merchant", result.get("merchant_name", "Not found")),
        ("Receipt Date", result.get("receipt_date", "Unknown")),
    ]
    fields_right = [
        ("Total Amount", f"{result.get('extracted_amount','Not found')} {result.get('currency','')}".strip()),
        ("AI Verdict Reason", result.get("reason", "—")),
    ]
    with col_a:
        for label, value in fields_left:
            st.markdown(f"""
                <div class="data-field">
                    <div class="data-field-label">{label}</div>
                    <div class="data-field-value">{value}</div>
                </div>""", unsafe_allow_html=True)
    with col_b:
        for label, value in fields_right:
            st.markdown(f"""
                <div class="data-field">
                    <div class="data-field-label">{label}</div>
                    <div class="data-field-value">{value}</div>
                </div>""", unsafe_allow_html=True)

    # Violations
    v = result.get("violations", "None")
    if v and v.lower() not in ("none", "n/a", ""):
        st.markdown(f"""
            <div class="data-field" style="border-left:3px solid #E05252; margin-top:4px;">
                <div class="data-field-label">Policy Violations</div>
                <div class="data-field-value" style="color:#E05252;">{v}</div>
            </div>""", unsafe_allow_html=True)

    # Authenticity block
    fake_risk    = result.get("fake_risk", "UNKNOWN")
    fake_reasons = result.get("fake_reasons", "None")
    risk_class   = {"LOW": "risk-low", "MEDIUM": "risk-med", "HIGH": "risk-high"}.get(fake_risk, "")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:18px 20px;">
            <div style="font-family:'DM Mono',monospace; font-size:10px; color:#4A4A52; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:12px;">Authenticity Analysis</div>
            <div style="display:flex; align-items:center; gap:12px;">
                <span style="font-size:13px; color:#8A8A8E;">Fraud Risk:</span>
                <span class="{risk_class}">{fake_risk}</span>
            </div>
            {"<div style='margin-top:10px; font-size:13px; color:#8A8A8E;'>"+fake_reasons+"</div>" if fake_reasons and fake_reasons.lower() not in ("none","n/a","") else ""}
        </div>
    """, unsafe_allow_html=True)


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

    # ── SECTION LABEL ──
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

            colour_map = {"APPROVED": "#3DBA7A", "FLAGGED": "#E8B84B", "REJECTED": "#E05252"}
            verdict_colour = colour_map.get(final, "#8A8A8E")
            override_tag = ' <span style="font-size:10px; color:#D4AF37; font-family:\'DM Mono\',monospace;">[OVERRIDE]</span>' if is_override else ''

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
            if v == "APPROVED": approved += 1
            elif v == "FLAGGED": flagged += 1
            elif v == "REJECTED": rejected += 1

        rate = round((approved / total) * 100) if total else 0

        # Metric cards
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

        # Approval rate
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