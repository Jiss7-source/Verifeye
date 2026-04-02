import streamlit as st
from auditor import audit_expense
from utils import get_file_content
from database import init_db, save_audit, get_all_audits

# --- Page Setup ---
st.set_page_config(
    page_title="Expense Auditor",
    page_icon="🧾",
    layout="wide"
)

# Initialize database
init_db()

# --- Header ---
st.title("🧾 Policy-First Expense Auditor")
st.write("Upload an expense receipt or report. Our AI will check it against company policy instantly.")

# --- Sidebar ---
with st.sidebar:
    st.header("📋 About")
    st.write("This tool audits expenses against company policy using Gemini AI.")
    st.divider()
    st.header("📁 Supported Files")
    st.write("✅ PDF files")
    st.write("✅ JPG / PNG images")

# --- File Upload Section ---
st.subheader("📤 Upload Your Expense")
uploaded_file = st.file_uploader(
    "Choose a receipt or expense report",
    type=["pdf", "jpg", "jpeg", "png"]
)

if uploaded_file:
    st.success(f"File uploaded: **{uploaded_file.name}**")

    if st.button("🔍 Audit This Expense", type="primary"):
        with st.spinner("Analyzing your expense against company policy..."):

            # Read the file
            content, content_type = get_file_content(uploaded_file)

            if content_type == "unsupported":
                st.error("❌ Unsupported file type. Please upload a PDF or image.")
            else:
                # Send to Gemini AI
                result = audit_expense(content, content_type)

                # Display result
                st.divider()
                st.subheader("📊 Audit Result")

                # Color the verdict
                if "APPROVED" in result.upper():
                    st.success("✅ VERDICT: APPROVED")
                elif "REJECTED" in result.upper():
                    st.error("❌ VERDICT: REJECTED")
                else:
                    st.warning("⚠️ VERDICT: NEEDS REVIEW")

                # Show full analysis
                st.markdown(result)

                # Save to database
                verdict = "APPROVED" if "APPROVED" in result.upper() else \
                          "REJECTED" if "REJECTED" in result.upper() else "NEEDS REVIEW"
                save_audit(uploaded_file.name, verdict, result[:300])

                st.info("💾 Audit saved to history!")

# --- Audit History Section ---
st.divider()
st.subheader("📚 Audit History")

history = get_all_audits()
if history:
    for row in history:
        id_, filename, verdict, summary, timestamp = row
        color = "🟢" if verdict == "APPROVED" else "🔴" if verdict == "REJECTED" else "🟡"
        with st.expander(f"{color} {filename} — {verdict} ({timestamp})"):
            st.write(summary)
else:
    st.write("No audits yet. Upload a receipt to get started!")