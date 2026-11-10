from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Project Documentation", layout="wide")

st.title("Project Documentation")

# Find Documentation.pdf in the main folder (one level above "pages")
pdf_path = Path(__file__).parent.parent / "Documentation.pdf"

if not pdf_path.exists():
    st.error("Documentation.pdf was not found in the repository.")
else:
    pdf_bytes = pdf_path.read_bytes()

    # Download button (always works)
    st.download_button(
        label="Download Documentation (PDF)",
        data=pdf_bytes,
        file_name="Documentation.pdf",
        mime="application/pdf",
    )

    # Show the PDF on the page (needs streamlit[pdf] in requirements.txt)
    try:
        st.pdf(pdf_bytes, height=800)
    except Exception:
        st.info("The PDF preview is not available here. Please use the download button above.")
