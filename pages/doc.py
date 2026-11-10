
import streamlit as st
import base64
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Project Documentation",
    page_icon="📄",
    layout="wide"
)

st.title("Z-Test Simulator Documentation")
st.write("Project report and documentation.")

# Locate the PDF in the root directory
pdf_path = Path(__file__).parent.parent / "Documentation.pdf"

if pdf_path.exists():

    with open(pdf_path, "rb") as file:
        pdf_bytes = file.read()

    # Display PDF
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    pdf_display = f"""
    <iframe
        src="data:application/pdf;base64,{base64_pdf}"
        width="100%"
        height="850"
        type="application/pdf">
    </iframe>
    """

    components.html(
        pdf_display,
        height=870,
        scrolling=True
    )

    # Download option
    st.download_button(
        label="Download Documentation PDF",
        data=pdf_bytes,
        file_name="Documentation.pdf",
        mime="application/pdf"
    )

else:
    st.error("Documentation.pdf not found!")
