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
#  CUSTOM CSS — THE EDITORIAL REWRITE
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    color: #1A1A1A;
    line-height: 1.75;
}
h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 600;
    color: #1A1A1A;
    letter-spacing: -0.01em;
}

/* Sidebar Radio Refactoring */
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    padding: 10px 16px;
    border-radius: 4px;
    border: 1px solid transparent;
    transition: all 0.2s ease;
    margin-bottom: 4px;
    background-color: transparent;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background-color: #FAFAF8;
    border: 1px solid #E8E4DF;
}
[data-testid="stSidebar"] div[role="radiogroup"] div[data-testid="stMarkdownContainer"] {
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    color: #1A1A1A !important;
}

/* Container Structure (Turning Streamlit Native Borders into Luxury Cards) */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border: 1px solid #E8E4DF !important;
    border-radius: 8px !important;
    padding: 24px 32px !important;
    margin-bottom: 12px !important;
    box-shadow: 0 1px 2px rgba(26,26,26,0.04) !important;
    transition: all 0.2s ease-out !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 4px 12px rgba(26,26,26,0.06) !important;
}

/* Minimalist Form Inputs */
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stDateInput>div>div>input {
    border: 0px !important;
    border-bottom: 1px solid #E8E4DF !important;
    background-color: transparent !important;
    border-radius: 0px !important;
    padding-left: 4px !important;
    font-family: 'Source Sans 3', sans-serif;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus, .stDateInput>div>div>input:focus {
    border-bottom: 2px solid #B8860B !important;
    box-shadow: none !important;
}

/* Small Caps Badges */
.badge-approved {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.15em;
    padding: 6px 16px; border-radius: 4px;
    background: #F5F8F5; color: #2D5A27; border: 1px solid #d4e5d2;
}
.badge-flagged  {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.15em;
    padding: 6px 16px; border-radius: 4px;
    background: #FFFBF0; color: #8C6200; border: 1px solid #F5E1A4;
}
.badge-rejected {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.15em;
    padding: 6px 16px; border-radius: 4px;
    background: #FFF5F5; color: #8A2E2E; border: 1px solid #F5D0D0;
}
.badge-error {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.15em;
    padding: 6px 16px; border-radius: 4px;
    background: #F5F3F0; color: #6B6B6B; border: 1px solid #E8E4DF;
}

/* Fake risk classes */
.fake-low  { color:#2D5A27; font-weight:600; }
.fake-med  { color:#B8860B; font-weight:600; }
.fake-high { color:#8A2E2E; font-weight:600; }

/* Dashboards Metrics */
.metric-box {
    background: #FFFFFF;
    border: 1px solid #E8E4DF;
    border-radius: 8px;
    padding: 24px 28px;
    text-align: center;
    box-shadow: 0 1px 2px rgba(26,26,26,0.04);
}
.metric-number {
    font-family: 'Playfair Display', serif;
    font-size: 40px;
    font-weight: 600;
    line-height: 1;
    color: #1A1A1A !important;
}
.metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: #6B6B6B;
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.15em;
}

.history-row {
    background: #FFFFFF;
    border: 1px solid #E8E4DF;
    border-radius: 6px;
    padding: 16px 20px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 15px;
    transition: all 0.2s ease-out;
}
.history-row:hover {
    box-shadow: 0 4px 12px rgba(26,26,26,0.04);
}

/* Primary Buttons */
.stButton > button {
    background: #B8860B;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 12px 28px;
    font-family: 'Source Sans 3', sans-serif;
    font-weight: 500;
    font-size: 15px;
    letter-spacing: 0.05em;
    cursor: pointer;
    box-shadow: 0 1px 2px rgba(184,134,11,0.2);
    transition: all 0.2s ease-out;
}
.stButton > button:hover {
    background: #D4A84B;
    box-shadow: 0 4px 12px rgba(184,134,11,0.3);
    transform: translateY(-2px);
    color: #FFFFFF;
}
.stButton > button:active {
    transform: translateY(0);
}

/* Rule lines */
hr { border-color: #E8E4DF; border-width: 1px; margin: 2rem 0; }
#MainMenu, footer { visibility: hidden; }

/* Override Dropzone */
[data-testid="stFileUploadDropzone"] {
    background-color: #FAFAF8;
    border: 1px dashed #B8860B !important;
    border-radius: 8px;
}
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
    ("single_result",  None),
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
        "<div style='font-size:11px;color:#6B6B6B;font-family:\"IBM Plex Mono\", monospace;text-transform:uppercase;letter-spacing:0.1em;text-align:center;'>"
        "Corporate Financial Controls<br>"
        "Powered by Gemini 2.5</div>",
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────
#  HELPER — render one result dict
# ─────────────────────────────────────────────
def display_result(result: dict):
    verdict = result.get("verdict", "ERROR")

    badge_map = {
        "APPROVED": ("badge-approved", "✔"),
        "FLAGGED":  ("badge-flagged",  "⚑"),
        "REJECTED": ("badge-rejected", "✘"),
    }
    badge_class, icon = badge_map.get(verdict, ("badge-error", "•"))

    st.markdown(
        f'<span class="{badge_class}">{icon} {verdict}</span>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**Extracted Merchant:** {result.get('merchant_name', 'Not found')}")
        st.markdown(f"**Extracted Date:** {result.get('receipt_date', 'Unknown')}")
    with col_b:
        amount = result.get('extracted_amount', 'Not found')
        cur = result.get('currency', '')
        st.markdown(f"**Extracted Total:** {amount} {cur}")
        st.markdown(f"**AI Reason:** {result.get('reason', '—')}")

    v = result.get("violations", "None")
    if v and v.lower() not in ("none", "n/a", ""):
        st.markdown(f"**Policy violations:** {v}")

    fake_risk    = result.get("fake_risk",    "UNKNOWN")
    fake_reasons = result.get("fake_reasons", "None")

    risk_colour = {"LOW": "fake-low", "MEDIUM": "fake-med", "HIGH": "fake-high"}.get(
        fake_risk, ""
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Authenticity Validation**")
    st.markdown(
        f'Risk Evaluation: '
        f'<span class="{risk_colour}">{fake_risk}</span>',
        unsafe_allow_html=True
    )
    if fake_reasons and fake_reasons.lower() not in ("none", "n/a", ""):
        st.markdown(f"*Signals detected:* {fake_reasons}")


# ═══════════════════════════════════════════════════════════════
#  PAGE 1 — The Audit Console
# ═══════════════════════════════════════════════════════════════
if page == "◆ Audit Console":
    
    # Hero Segment
    st.markdown("""
        <div style="text-align: center; margin-top: 4rem; margin-bottom: 4rem;">
            <h1 style="font-size: 4.5rem; line-height: 1.1; margin-bottom: 1rem; color: #1A1A1A">The Audit Console</h1>
            <p style="font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem; color: #B8860B; letter-spacing: 0.15em; text-transform: uppercase;">Intelligent compliance. Zero friction.</p>
        </div>
    """, unsafe_allow_html=True)

    # Main Grid (Left side: Pillar Cards + Image, Right side: Form)
    col1, spacer, col2 = st.columns([1.3, 0.1, 1.1])

    with col1:
        st.markdown("<div class='mb-6 flex items-center gap-4'><span class='h-px flex-1 bg-[var(--border)]'></span><span class='small-caps' style='color:#B8860B; border-bottom: 1px solid #E8E4DF; margin-bottom: 1rem'>SYSTEM ARCHITECTURE</span></div>", unsafe_allow_html=True)
        
        # We explicitly wrap in st.container(border=True) to invoke the .card CSS styling.
        with st.container(border=True):
            st.markdown("<h3 style='font-family: \"Playfair Display\", serif; margin-bottom: 0.2rem'>1. Policy Intelligence</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #6B6B6B; font-size: 0.95rem; margin-bottom: 0px;'>Cross-references complex organizational constraints automatically. Analyzes context against live thresholds.</p>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("<h3 style='font-family: \"Playfair Display\", serif; margin-bottom: 0.2rem'>2. Fraud Mitigation</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #6B6B6B; font-size: 0.95rem; margin-bottom: 0px;'>Advanced OCR parses merchant validation, timing anomalies, blurry uploads, and explicitly mathematical discrepancies.</p>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("<h3 style='font-family: \"Playfair Display\", serif; margin-bottom: 0.2rem'>3. Immutable Ledger</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #6B6B6B; font-size: 0.95rem; margin-bottom: 0px;'>Centralized routing supporting human-in-the-loop exception tracking and resolution oversight.</p>", unsafe_allow_html=True)
            
        try:
            img = Image.open(r"C:\Users\jizzm\.gemini\antigravity\brain\1ceb6c75-5044-4816-be42-7b13041b56c6\ledger_illustration_1775494877884.png")
            st.image(img, use_container_width=True)
        except Exception:
            pass

    with col2:
        st.markdown("<div class='mb-6 flex items-center gap-4'><span class='h-px flex-1 bg-[var(--border)]'></span><span class='small-caps' style='color:#B8860B; border-bottom: 1px solid #E8E4DF; margin-bottom: 1rem'>TRANSACTION INGESTION</span></div>", unsafe_allow_html=True)
        
        # Form Container 
        with st.container(border=True):
            claimed_date = st.date_input("Claimed Expense Date", value=datetime.date.today())
            st.markdown("<br>", unsafe_allow_html=True)
            
            business_purpose = st.text_area("Business Context", placeholder="Define the organizational requirement supporting this spend.", height=100)
            st.markdown("<br>", unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Document Upload",
                type=["pdf", "jpg", "jpeg", "png"],
                key="single_uploader",
                label_visibility="collapsed"
            )

        if st.button("Execute Compliance Frame", key="btn_single", use_container_width=True):
            if not uploaded_file:
                st.warning("⚠️ Provide evidence prior to execution.")
            elif not business_purpose:
                st.warning("⚠️ Business Context is strictly required per policy framing.")
            else:
                with st.spinner("Deconstructing and evaluating..."):
                    content, kind = get_file_content(uploaded_file)

                    if kind == "unsupported" or kind.startswith("error") or kind == "empty":
                        st.error("❌ Document is incompatible or unreadable.")
                        st.stop()

                    mime_type = uploaded_file.type if kind == "image" else "image/jpeg"

                    result = audit_receipt(
                        content=content,
                        content_type=kind,
                        policy_text=policy_text,
                        filename=uploaded_file.name,
                        claimed_date=str(claimed_date),
                        business_purpose=business_purpose,
                        mime_type=mime_type
                    )
                    save_audit(uploaded_file.name, business_purpose, str(claimed_date), result["verdict"], result["reason"])
                    st.session_state.single_result = result

    # Display results
    if st.session_state.single_result:
        st.markdown("<hr>", unsafe_allow_html=True)
        col4, col5, col6 = st.columns([1, 4, 1])
        with col5:
            with st.container(border=True):
                st.markdown("### Compliance Results Table")
                st.markdown("<br>", unsafe_allow_html=True)
                display_result(st.session_state.single_result)


# ═══════════════════════════════════════════════════════════════
#  PAGE 2 — LEDGER & HISTORY
# ═══════════════════════════════════════════════════════════════
elif page == "◇ Ledger & History":
    st.markdown("""
        <div style="margin-top: 2rem; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem; line-height: 1.1;">Ledger & Overrides</h1>
            <p style="font-family: 'Source Sans 3', sans-serif; color: #6B6B6B;">Comprehensive system logs and human-in-the-loop intervention portal.</p>
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
            "<div class='card' style='text-align:center;color:#6b7280;'>"
            "Void ledger. No entries currently logged."
            "</div>",
            unsafe_allow_html=True
        )
    else:
        for row in rows:
            row_id = row['id']
            filename = row['filename']
            ai_verdict = row['verdict']
            final_verdict = row['human_verdict'] if row.get('human_verdict') else ai_verdict
            summary = row['summary']
            timestamp = row['timestamp']
            
            display_status = f"{final_verdict}"
            if row.get('human_verdict'):
                display_status += " [OVERRIDE]"

            with st.expander(f"Tx #{row_id}: {filename}  —  {display_status}", expanded=False):
                st.markdown(f"**AI Inference Verdict:** {ai_verdict}")
                st.markdown(f"**Policy Reason:** {summary}")
                st.markdown(f"**Execution Date:** {row.get('claimed_date', 'N/A')}")
                st.markdown(f"**Purpose Statement:** {row.get('business_purpose', 'N/A')}")
                
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("<span class='small-caps'>HUMAN SUPERVISOR OVERRIDE</span>", unsafe_allow_html=True)
                
                with st.form(key=f"form_override_{row_id}"):
                    current_comment = row.get('human_comment', '')
                    new_comment = st.text_input("Override Justification", value=current_comment if current_comment else "", key=f"comment_{row_id}")
                    new_verdict = st.selectbox("Force State Transition", ["", "APPROVED", "FLAGGED", "REJECTED"], key=f"verdict_{row_id}")
                    
                    submit = st.form_submit_button("Commit Intervention")
                    if submit:
                        update_audit_override(row_id, new_comment, new_verdict if new_verdict else None)
                        st.success("State successfully patched.")
                        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    if rows:
        if st.button("Purge Operating Ledger"):
            delete_all_audits()
            st.success("Ledger neutralized.")
            st.rerun()


# ═══════════════════════════════════════════════════════════════
#  PAGE 3 — FINANCIAL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════
elif page == "⸬ Financial Intelligence":
    st.markdown("""
        <div style="margin-top: 2rem; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem; line-height: 1.1;">Intelligence Overview</h1>
            <p style="font-family: 'Source Sans 3', sans-serif; color: #6B6B6B;">Real-time metrics accounting for human interventions.</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    all_rows = get_all_audits()

    if not all_rows:
        st.markdown(
            "<div class='card' style='text-align:center;color:#6b7280;'>"
            "Insufficient data points."
            "</div>",
            unsafe_allow_html=True
        )
    else:
        total    = len(all_rows)
        approved = 0
        flagged = 0
        rejected = 0
        
        for r in all_rows:
            v = r.get('human_verdict') if r.get('human_verdict') else r['verdict']
            if v == "APPROVED": approved += 1
            elif v == "FLAGGED": flagged += 1
            elif v == "REJECTED": rejected += 1

        col1, col2, col3, col4 = st.columns(4)
        for col, label, value, colour in [
            (col1, "Total Processed", total,    "#1A1A1A"),
            (col2, "Approved",        approved, "#2D5A27"),
            (col3, "Flagged",         flagged,  "#B8860B"),
            (col4, "Rejected",        rejected, "#8A2E2E"),
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
        st.markdown("<span class='small-caps'>LATEST TRAFFIC</span>", unsafe_allow_html=True)

        for row in all_rows[:5]:
            filename = row['filename']
            v = row.get('human_verdict') if row.get('human_verdict') else row['verdict']
            timestamp = row['timestamp']
            
            colour = {
                "APPROVED": "#2D5A27",
                "FLAGGED":  "#B8860B",
                "REJECTED": "#8A2E2E",
            }.get(v, "#1A1A1A")
            st.markdown(f"""
<div class='history-row'>
  <span style='color:{colour};font-weight:600;min-width:90px'>{v}</span>
  <span style='flex:1'>{filename}</span>
  <span style='color:#6b7280;font-size:12px'>{timestamp}</span>
</div>""", unsafe_allow_html=True)