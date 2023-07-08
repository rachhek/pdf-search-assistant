import streamlit as st
from pathlib import Path
import base64
# Hardcoded path to the PDF file
pdf_path = Path("data/layout.sample.pdf")
st.set_page_config(layout="wide",page_title="PDF search assistant",page_icon="🔍",initial_sidebar_state="collapsed")
col1, col2 = st.columns([1, 1])

def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=0&navpanes=0" height="375" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

def get_pdf_parts(file):
    return "hello"

# Streamlit app
def app():
    with col1:
        displayPDF(pdf_path)
    with col2:

        st.header("hello")

if __name__ == "__main__":
    app()