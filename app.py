# ─────────────────────────────────────────────
#  PAGE CONFIG — must be the ABSOLUTE FIRST Streamlit call
# ─────────────────────────────────────────────
import streamlit as st
import datetime

st.set_page_config(
    page_title="Expense Auditor",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  IMPORTS  (only after set_page_config)
# ─────────────────────────────────────────────
from io import BytesIO
from PIL import Image

from utils import get_file_content, load_policy_text
from database import (
    init_db, save_audit, update_audit_override,
    get_all_audits, get_flagged_audits, delete_all_audits
)
from auditor import audit_receipt

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@400;500;600&display=swap');

/* ── PAGE ENTRANCE ANIMATION ── */
@keyframes pageFadeIn {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
section.main > div {
  animation: pageFadeIn 0.7s cubic-bezier(0.22,1,0.36,1) both;
}

/* ── HERO TITLE ENTRANCE ── */
@keyframes heroReveal {
  from { opacity: 0; letter-spacing: 0.3em; }
  to   { opacity: 1; letter-spacing: -0.01em; }
}
.hero-title {
  animation: heroReveal 1s cubic-bezier(0.22,1,0.36,1) 0.2s both;
}

/* ── SIDEBAR ENTRANCE ── */
@keyframes sideSlide {
  from { opacity: 0; transform: translateX(-20px); }
  to   { opacity: 1; transform: translateX(0); }
}
[data-testid="stSidebar"] {
  animation: sideSlide 0.6s cubic-bezier(0.22,1,0.36,1) 0.1s both;
}

/* ── AMBIENT GLOW ── */
.ambient-glow {
    position: absolute; top: -150px; left: 50%;
    transform: translateX(-50%);
    width: 900px; height: 900px;
    background: radial-gradient(circle, rgba(184,134,11,0.06) 0%, rgba(250,250,248,0) 70%);
    z-index: -10; pointer-events: none;
}

/* ── BASE ── */
.stApp {
    background-color: #FAFAF8 !important;
}
html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    color: #1A1A1A; line-height: 1.75;
}
h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 600; color: #1A1A1A; letter-spacing: -0.01em;
}

/* ── SIDEBAR RADIO ── */
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none !important; }
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    padding: 10px 16px; border-radius: 4px;
    border: 1px solid transparent; transition: all 0.2s ease; margin-bottom: 4px;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background-color: #FAFAF8; border: 1px solid #E8E4DF;
}
[data-testid="stSidebar"] div[role="radiogroup"] div[data-testid="stMarkdownContainer"] {
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 16px !important; font-weight: 500 !important; color: #1A1A1A !important;
}

/* ── CARDS ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important; border: 1px solid #E8E4DF !important;
    border-radius: 8px !important; padding: 24px 32px !important;
    margin-bottom: 12px !important; box-shadow: 0 1px 2px rgba(26,26,26,0.04) !important;
    transition: all 0.2s ease-out !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 8px 24px rgba(26,26,26,0.08) !important;
    border: 1px solid rgba(184,134,11,0.5) !important;
    transform: translateY(-2px);
}

/* ── INPUTS ── */
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stDateInput>div>div>input {
    border: 0px !important; border-bottom: 1px solid #E8E4DF !important;
    background-color: transparent !important; border-radius: 0px !important;
    padding-left: 4px !important; font-family: 'Source Sans 3', sans-serif;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus, .stDateInput>div>div>input:focus {
    border-bottom: 2px solid #B8860B !important; box-shadow: none !important;
}

/* ── METRIC BOXES ── */
.metric-box {
    background: #FFFFFF; border: 1px solid #E8E4DF; border-radius: 8px;
    padding: 24px 28px; text-align: center; box-shadow: 0 1px 2px rgba(26,26,26,0.04);
}
.metric-number { font-family: 'Playfair Display', serif; font-size: 40px; font-weight: 600; line-height: 1; color: #1A1A1A !important; }
.metric-label  { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: #6B6B6B; margin-top: 8px; text-transform: uppercase; letter-spacing: 0.15em; }

/* ── HISTORY ROW ── */
.history-row {
    background: #FFFFFF; border: 1px solid #E8E4DF; border-radius: 6px;
    padding: 16px 20px; margin-bottom: 8px; display: flex;
    align-items: center; gap: 16px; font-size: 15px; transition: all 0.2s ease-out;
}
.history-row:hover { box-shadow: 0 4px 12px rgba(26,26,26,0.04); }

/* ── BUTTONS ── */
.stButton > button {
    background: #B8860B; color: #FFFFFF; border: none; border-radius: 6px;
    padding: 12px 28px; font-family: 'Source Sans 3', sans-serif; font-weight: 500;
    font-size: 15px; letter-spacing: 0.05em; cursor: pointer;
    box-shadow: 0 1px 2px rgba(184,134,11,0.2); transition: all 0.2s ease-out;
}
.stButton > button:hover {
    background: #D4A84B; box-shadow: 0 4px 12px rgba(184,134,11,0.3);
    transform: translateY(-2px); color: #FFFFFF;
}
.stButton > button:active { transform: translateY(0); }

hr { border-color: #E8E4DF; border-width: 1px; margin: 2rem 0; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stFileUploadDropzone"] {
    background-color: #FAFAF8;
    border: 1px dashed #B8860B !important; border-radius: 8px;
}

/* ═══════════════════════════════════════════════
   RESULT CARD — Traffic-light verdict display
═══════════════════════════════════════════════ */

/* Entrance animation for each result card */
@keyframes resultSlideIn {
  from { opacity: 0; transform: translateY(28px); }
  to   { opacity: 1; transform: translateY(0); }
}

.result-card {
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    animation: resultSlideIn 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
}

/* ── Header band (coloured) ── */
.card-header {
    padding: 20px 24px 18px;
    display: flex; align-items: center; gap: 16px;
    position: relative; overflow: hidden;
}
.card-header::after {
    content: '';
    position: absolute; inset: 0;
    background: rgba(255,255,255,0.06);
    animation: headerPulse 2.8s ease-in-out infinite;
}
@keyframes headerPulse {
  0%, 100% { opacity: 0; }
  50%       { opacity: 1; }
}

/* Traffic-light gradient headers */
.approved-header { background: linear-gradient(135deg, #1a6b2f 0%, #2e8b57 100%); }
.flagged-header  { background: linear-gradient(135deg, #b45309 0%, #d97706 100%); }
.rejected-header { background: linear-gradient(135deg, #8b1a1a 0%, #c0392b 100%); }
.error-header    { background: linear-gradient(135deg, #374151 0%, #6b7280 100%); }

/* Signal light dot */
.signal-dot {
    width: 52px; height: 52px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0; position: relative; z-index: 1;
    background: rgba(255,255,255,0.18);
}
.signal-approved {
    box-shadow: 0 0 0 3px rgba(255,255,255,0.25), 0 0 20px rgba(52,211,120,0.6);
    animation: greenGlow 2s ease-in-out infinite;
}
.signal-flagged {
    box-shadow: 0 0 0 3px rgba(255,255,255,0.25), 0 0 20px rgba(251,191,36,0.7);
    animation: amberGlow 1.5s ease-in-out infinite;
}
.signal-rejected {
    box-shadow: 0 0 0 3px rgba(255,255,255,0.25), 0 0 20px rgba(239,68,68,0.7);
    animation: redGlow 1.2s ease-in-out infinite;
}
@keyframes greenGlow {
  0%, 100% { box-shadow: 0 0 0 3px rgba(255,255,255,0.25), 0 0 16px rgba(52,211,120,0.4); }
  50%       { box-shadow: 0 0 0 3px rgba(255,255,255,0.35), 0 0 28px rgba(52,211,120,0.8); }
}
@keyframes amberGlow {
  0%, 100% { box-shadow: 0 0 0 3px rgba(255,255,255,0.25), 0 0 16px rgba(251,191,36,0.5); }
  50%       { box-shadow: 0 0 0 3px rgba(255,255,255,0.35), 0 0 28px rgba(251,191,36,0.9); }
}
@keyframes redGlow {
  0%, 100% { box-shadow: 0 0 0 3px rgba(255,255,255,0.25), 0 0 16px rgba(239,68,68,0.5); }
  50%       { box-shadow: 0 0 0 3px rgba(255,255,255,0.35), 0 0 30px rgba(239,68,68,1); }
}

.verdict-label-sm {
    font-family: 'IBM Plex Mono', monospace; font-size: 11px;
    letter-spacing: 0.18em; text-transform: uppercase;
    color: rgba(255,255,255,0.65); margin-bottom: 3px; z-index: 1; position: relative;
}
.verdict-word {
    font-family: 'Playfair Display', serif; font-size: 28px;
    font-weight: 700; color: #fff; line-height: 1;
    z-index: 1; position: relative;
}

/* ── Card body (white) ── */
.card-body {
    background: #ffffff;
    border: 1px solid #e5e7eb; border-top: none;
    border-radius: 0 0 16px 16px;
    padding: 22px 24px;
}

/* Reason banners */
.reason-banner {
    padding: 12px 16px; border-radius: 10px;
    font-size: 14px; line-height: 1.55; margin-bottom: 18px; font-weight: 500;
}
.reason-approved { background:#f0faf4; color:#1a5c30; border-left: 3px solid #2e8b57; }
.reason-flagged  { background:#fffbeb; color:#7c4a03; border-left: 3px solid #d97706; }
.reason-rejected { background:#fff5f5; color:#7a1c1c; border-left: 3px solid #c0392b; }
.reason-error    { background:#f3f4f6; color:#374151; border-left: 3px solid #9ca3af; }

/* Warning callout (FLAGGED only) */
.warning-callout {
    display: flex; align-items: flex-start; gap: 10px;
    background: #fffbeb; border: 1px solid #fcd34d; border-radius: 8px;
    padding: 10px 14px; margin-bottom: 16px; font-size: 13px; color: #92400e;
}

/* Data grid */
.data-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 18px;
}
.data-cell {
    background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px 14px;
}
.data-cell-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 10px;
    letter-spacing: 0.12em; text-transform: uppercase; color: #9ca3af; margin-bottom: 4px;
}
.data-cell-value { font-size: 14px; font-weight: 500; color: #111827; }
.cell-ok   { color: #2e8b57 !important; }
.cell-warn { color: #b45309 !important; }
.cell-bad  { color: #c0392b !important; }

/* Divider */
.rc-divider { border: none; border-top: 1px solid #f3f4f6; margin: 14px 0; }

/* Fraud row */
.fraud-row { display: flex; align-items: center; gap: 10px; font-size: 13px; margin-bottom: 6px; }
.fraud-label { color: #6b7280; }
.risk-badge {
    font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 500;
    letter-spacing: 0.1em; text-transform: uppercase; padding: 3px 10px; border-radius: 20px;
}
.risk-low  { background:#f0faf4; color:#1a5c30; border: 1px solid #a7f3d0; }
.risk-med  { background:#fffbeb; color:#7c4a03; border: 1px solid #fcd34d; }
.risk-high { background:#fff5f5; color:#7a1c1c; border: 1px solid #fca5a5; }
.fraud-signals { font-size: 12px; color: #6b7280; padding-left: 4px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  STARTUP
# ─────────────────────────────────────────────
init_db()

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
for key, default in [
    ("single_result", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Playfair Auditor")
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("### 📄 Policy Ruleset")
    policy_source = st.radio(
        "Policy source",
        ["Use built-in framework", "Upload custom parameters"],
        label_visibility="collapsed"
    )

    if policy_source == "Upload custom parameters":
        policy_upload = st.file_uploader(
            "Upload policy PDF",
            type=["pdf"],
            key="policy_uploader"
        )
        if policy_upload:
            try:
                import fitz
                raw_pol = policy_upload.read()
                doc = fitz.open(stream=raw_pol, filetype="pdf")
                policy_text = "\n".join(p.get_text() for p in doc)
                doc.close()
                policy_status = "ok"
            except Exception as e:
                policy_text, policy_status = load_policy_text()
        else:
            policy_text, policy_status = load_policy_text()
    else:
        @st.cache_data
        def _load_builtin():
            return load_policy_text()
        policy_text, policy_status = _load_builtin()

    st.markdown("<hr>", unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["◆ Audit Console", "◇ Ledger & History", "⸬ Financial Intelligence"],
        label_visibility="collapsed"
    )

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:11px;color:#6B6B6B;font-family:\"IBM Plex Mono\", monospace;"
        "text-transform:uppercase;letter-spacing:0.1em;text-align:center;'>"
        "Corporate Financial Controls<br>Powered by Gemini 2.5</div>",
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────
#  HELPER — render one result dict  (REDESIGNED)
# ─────────────────────────────────────────────
def display_result(result: dict):
    verdict = result.get("verdict", "ERROR").upper()

    # ── Traffic-light config ──────────────────
    config = {
        "APPROVED": {
            "header_class": "approved-header",
            "signal_class":  "signal-dot signal-approved",
            "icon":          "✔",
            "reason_class":  "reason-approved",
            "viol_color":    "cell-ok",
        },
        "FLAGGED": {
            "header_class": "flagged-header",
            "signal_class":  "signal-dot signal-flagged",
            "icon":          "⚑",
            "reason_class":  "reason-flagged",
            "viol_color":    "cell-warn",
        },
        "REJECTED": {
            "header_class": "rejected-header",
            "signal_class":  "signal-dot signal-rejected",
            "icon":          "✘",
            "reason_class":  "reason-rejected",
            "viol_color":    "cell-bad",
        },
    }.get(verdict, {
        "header_class": "error-header",
        "signal_class":  "signal-dot",
        "icon":          "•",
        "reason_class":  "reason-error",
        "viol_color":    "",
    })

    merchant = result.get("merchant_name",    "Not found")
    rec_date = result.get("receipt_date",     "Not found")
    amount   = result.get("extracted_amount", "Not found")
    currency = result.get("currency",         "")
    reason   = result.get("reason",           "—")
    viol     = result.get("violations",       "None")
    fake_r   = result.get("fake_risk",        "UNKNOWN").upper()
    fake_sig = result.get("fake_reasons",     "None")

    def _clean(val: str) -> str:
        """Strip Python list/dict formatting the AI may accidentally return."""
        import re, html as html_lib
        v = str(val).strip()
        # If AI returned a Python list like ['item1', 'item2'], unwrap it
        if v.startswith('[') and v.endswith(']'):
            inner = v[1:-1]
            # Remove surrounding quotes from each item and join with semicolons
            items = [i.strip().strip("'").strip('"') for i in inner.split("',") if i.strip()]
            if not items:  # fallback for single-item list
                items = [inner.strip().strip("'").strip('"')]
            v = "; ".join(i for i in items if i)
        # Escape any remaining HTML-unsafe characters
        return html_lib.escape(v)

    # Clean and sanitize all displayed values
    merchant = _clean(merchant)
    rec_date = _clean(rec_date)
    reason   = _clean(reason)
    viol     = _clean(viol)
    fake_sig = _clean(fake_sig)
    full_amount = _clean(f"{amount} {currency}".strip())

    # violation colour
    viol_colour = ""
    if viol and viol.lower() not in ("none", "n/a", ""):
        viol_colour = config["viol_color"]
    else:
        viol_colour = "cell-ok"
        viol = "None"

    # fake risk badge class
    risk_class = {"LOW": "risk-low", "MEDIUM": "risk-med", "HIGH": "risk-high"}.get(fake_r, "risk-low")

    # ── Warning callout for FLAGGED ───────────
    warning_html = ""
    if verdict == "FLAGGED":
        warning_html = """
        <div class="warning-callout">
          <span style="font-size:16px;flex-shrink:0;margin-top:1px;">&#9888;</span>
          <span>This claim requires human review before processing. Do not reimburse until
          an authorised supervisor has verified the discrepancy noted below.</span>
        </div>"""

    # ── Fraud signals line ────────────────────
    signals_html = ""
    if fake_sig and fake_sig.lower() not in ("none", "n/a", ""):
        signals_html = f'<div class="fraud-signals">Signals detected: {fake_sig}</div>'

    html = f"""
<div class="result-card">
  <div class="card-header {config['header_class']}">
    <div class="{config['signal_class']}">{config['icon']}</div>
    <div>
      <div class="verdict-label-sm">Audit verdict</div>
      <div class="verdict-word">{verdict.title()}</div>
    </div>
  </div>

  <div class="card-body">
    {warning_html}
    <div class="reason-banner {config['reason_class']}">{reason}</div>

    <div class="data-grid">
      <div class="data-cell">
        <div class="data-cell-label">Merchant</div>
        <div class="data-cell-value">{merchant}</div>
      </div>
      <div class="data-cell">
        <div class="data-cell-label">Receipt Date</div>
        <div class="data-cell-value">{rec_date}</div>
      </div>
      <div class="data-cell">
        <div class="data-cell-label">Extracted Total</div>
        <div class="data-cell-value">{full_amount}</div>
      </div>
      <div class="data-cell">
        <div class="data-cell-label">Policy Violations</div>
        <div class="data-cell-value {viol_colour}">{viol}</div>
      </div>
    </div>

    <hr class="rc-divider">

    <div class="fraud-row">
      <span class="fraud-label">Authenticity check:</span>
      <span class="risk-badge {risk_class}">{fake_r.replace('UNKNOWN','—')} risk</span>
    </div>
    {signals_html}
  </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE 1 — The Audit Console
# ═══════════════════════════════════════════════════════════════
if page == "◆ Audit Console":

    st.markdown('<div class="ambient-glow"></div>', unsafe_allow_html=True)

    # ── HERO ──
    col_img, spacer, col_text = st.columns([1, 0.1, 2])
    with col_img:
        try:
            img = Image.open("assets/hero.png")   # put your illustration here
            st.image(img, use_container_width=True)
        except Exception:
            pass
    with col_text:
        st.markdown('''
            <div style="margin-top: 2rem;">
                <h1 class="hero-title" style="font-size:5.5rem;line-height:1;margin-bottom:0.5rem;
                    color:#1A1A1A;font-family:'Playfair Display',serif;">VerifEYE</h1>
                <p style="font-family:'IBM Plex Mono',monospace;font-size:0.9rem;color:#B8860B;
                    letter-spacing:0.15em;text-transform:uppercase;">
                    Intelligent compliance. Zero friction.</p>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── TRANSACTION AREA ──
    st.markdown(
        "<span style='color:#B8860B;border-bottom:1px solid #E8E4DF;margin-bottom:1rem;"
        "width:100%;text-align:center;display:block;font-family:\"IBM Plex Mono\",monospace;"
        "font-size:12px;letter-spacing:0.18em;text-transform:uppercase;'>"
        "TRANSACTION INGESTION</span>",
        unsafe_allow_html=True
    )

    col_l, col_m, col_r = st.columns([1, 3, 1])
    with col_m:
        with st.container(border=True):
            claimed_date = st.date_input("Claimed Expense Date", value=datetime.date.today())
            st.markdown("<br>", unsafe_allow_html=True)

            business_purpose = st.text_area(
                "Business Context",
                placeholder="Define the organisational requirement supporting this spend.",
                height=100
            )
            st.markdown("<br>", unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Document Upload",
                type=["pdf", "jpg", "jpeg", "png"],
                key="single_uploader",
                label_visibility="collapsed"
            )

            submit_doc = st.button(
                "Execute Compliance Frame", key="btn_single", use_container_width=True
            )

    # ── Logic ──
    if submit_doc:
        if not uploaded_file:
            st.warning("⚠️ Provide evidence prior to execution.")
        elif not business_purpose:
            st.warning("⚠️ Business Context is strictly required per policy framing.")
        else:
            with st.spinner("Deconstructing and evaluating…"):
                content_bytes, kind = get_file_content(uploaded_file)

                if kind in ("unsupported", "empty") or kind.startswith("error"):
                    st.error("❌ Document is incompatible or unreadable.")
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
                save_audit(
                    uploaded_file.name, business_purpose,
                    str(claimed_date), result["verdict"], result["reason"]
                )
                st.session_state.single_result = result

    # ── Results area ──
    if st.session_state.single_result:
        st.markdown("<br>", unsafe_allow_html=True)
        col_la, col_ma, col_ra = st.columns([1, 3, 1])
        with col_ma:
            display_result(st.session_state.single_result)

    st.markdown("<br><br><br><br>", unsafe_allow_html=True)

    # ── ARCHITECTURE PILLARS ──
    st.markdown(
        "<span style='color:#B8860B;border-bottom:1px solid #E8E4DF;margin-bottom:1rem;"
        "width:100%;text-align:center;display:block;font-family:\"IBM Plex Mono\",monospace;"
        "font-size:12px;letter-spacing:0.18em;text-transform:uppercase;'>"
        "SYSTEM ARCHITECTURE</span>",
        unsafe_allow_html=True
    )
    p1, p2, p3 = st.columns(3)
    with p1:
        with st.container(border=True):
            st.markdown("<h3 style='font-family:\"Playfair Display\",serif;margin-bottom:0.2rem'>1. Policy Intelligence</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color:#6B6B6B;font-size:0.95rem;margin-bottom:0;'>Cross-references complex organisational constraints automatically.</p>", unsafe_allow_html=True)
    with p2:
        with st.container(border=True):
            st.markdown("<h3 style='font-family:\"Playfair Display\",serif;margin-bottom:0.2rem'>2. Fraud Mitigation</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color:#6B6B6B;font-size:0.95rem;margin-bottom:0;'>Advanced OCR parses merchant validation, timing anomalies, blurry uploads.</p>", unsafe_allow_html=True)
    with p3:
        with st.container(border=True):
            st.markdown("<h3 style='font-family:\"Playfair Display\",serif;margin-bottom:0.2rem'>3. Immutable Ledger</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color:#6B6B6B;font-size:0.95rem;margin-bottom:0;'>Centralised routing supporting human-in-the-loop exception tracking.</p>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE 2 — LEDGER & HISTORY
# ═══════════════════════════════════════════════════════════════
elif page == "◇ Ledger & History":
    st.markdown("""
        <div style="margin-top:2rem;margin-bottom:2rem;">
            <h1 style="font-size:2.5rem;line-height:1.1;">Ledger & Overrides</h1>
            <p style="font-family:'Source Sans 3',sans-serif;color:#6B6B6B;">
                Comprehensive system logs and human-in-the-loop intervention portal.</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    filter_choice = st.selectbox(
        "Visibility Filter",
        ["All Executions", "Anomalies (Flagged & Rejected)"]
    )
    rows = (
        get_flagged_audits()
        if filter_choice == "Anomalies (Flagged & Rejected)"
        else get_all_audits()
    )

    if not rows:
        st.markdown(
            "<div style='text-align:center;color:#6b7280;padding:2rem;'>"
            "Void ledger. No entries currently logged.</div>",
            unsafe_allow_html=True
        )
    else:
        for row in rows:
            row_id      = row['id']
            filename    = row['filename']
            ai_verdict  = row['verdict']
            final_v     = row['human_verdict'] if row.get('human_verdict') else ai_verdict
            summary     = row['summary']

            label = f"Tx #{row_id}: {filename}  —  {final_v}"
            if row.get('human_verdict'):
                label += " [OVERRIDE]"

            with st.expander(label, expanded=False):
                st.markdown(f"**AI Inference Verdict:** {ai_verdict}")
                st.markdown(f"**Policy Reason:** {summary}")
                st.markdown(f"**Execution Date:** {row.get('claimed_date', 'N/A')}")
                st.markdown(f"**Purpose Statement:** {row.get('business_purpose', 'N/A')}")
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown(
                    "<span style='font-family:\"IBM Plex Mono\",monospace;font-size:11px;"
                    "letter-spacing:0.15em;text-transform:uppercase;'>HUMAN SUPERVISOR OVERRIDE</span>",
                    unsafe_allow_html=True
                )
                with st.form(key=f"form_override_{row_id}"):
                    current_comment = row.get('human_comment', '')
                    new_comment = st.text_input(
                        "Override Justification",
                        value=current_comment if current_comment else "",
                        key=f"comment_{row_id}"
                    )
                    new_verdict = st.selectbox(
                        "Force State Transition",
                        ["", "APPROVED", "FLAGGED", "REJECTED"],
                        key=f"verdict_{row_id}"
                    )
                    submit = st.form_submit_button("Commit Intervention")
                    if submit:
                        update_audit_override(row_id, new_comment, new_verdict if new_verdict else None)
                        st.success("State successfully patched.")
                        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    if rows:
        if st.button("Purge Operating Ledger"):
            delete_all_audits()
            st.success("Ledger neutralised.")
            st.rerun()


# ═══════════════════════════════════════════════════════════════
#  PAGE 3 — FINANCIAL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════
elif page == "⸬ Financial Intelligence":
    st.markdown("""
        <div style="margin-top:2rem;margin-bottom:2rem;">
            <h1 style="font-size:2.5rem;line-height:1.1;">Intelligence Overview</h1>
            <p style="font-family:'Source Sans 3',sans-serif;color:#6B6B6B;">
                Real-time metrics accounting for human interventions.</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    all_rows = get_all_audits()

    if not all_rows:
        st.markdown(
            "<div style='text-align:center;color:#6b7280;padding:2rem;'>"
            "Insufficient data points.</div>",
            unsafe_allow_html=True
        )
    else:
        total = len(all_rows)
        approved = flagged = rejected = 0
        for r in all_rows:
            v = r.get('human_verdict') if r.get('human_verdict') else r['verdict']
            if v == "APPROVED": approved += 1
            elif v == "FLAGGED": flagged  += 1
            elif v == "REJECTED": rejected += 1

        col1, col2, col3, col4 = st.columns(4)
        for col, label, value, colour in [
            (col1, "Total Processed", total,    "#1A1A1A"),
            (col2, "Approved",        approved, "#2e8b57"),
            (col3, "Flagged",         flagged,  "#d97706"),
            (col4, "Rejected",        rejected, "#c0392b"),
        ]:
            with col:
                st.markdown(
                    f"<div class='metric-box'>"
                    f"<div class='metric-number' style='color:{colour} !important;'>{value}</div>"
                    f"<div class='metric-label'>{label}</div></div>",
                    unsafe_allow_html=True
                )

        st.markdown("<br>", unsafe_allow_html=True)
        rate = round((approved / total) * 100) if total else 0
        st.markdown(f"**Execution Flow Success:** `{rate}%`")
        st.progress(rate / 100)

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            "<span style='font-family:\"IBM Plex Mono\",monospace;font-size:11px;"
            "letter-spacing:0.15em;text-transform:uppercase;'>LATEST TRAFFIC</span>",
            unsafe_allow_html=True
        )
        for row in all_rows[:5]:
            filename = row['filename']
            v = row.get('human_verdict') if row.get('human_verdict') else row['verdict']
            timestamp = row['timestamp']
            colour = {"APPROVED":"#2e8b57","FLAGGED":"#d97706","REJECTED":"#c0392b"}.get(v,"#1A1A1A")
            st.markdown(f"""
<div class='history-row'>
  <span style='color:{colour};font-weight:600;min-width:90px'>{v}</span>
  <span style='flex:1'>{filename}</span>
  <span style='color:#6b7280;font-size:12px'>{timestamp}</span>
</div>""", unsafe_allow_html=True)
