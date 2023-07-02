import streamlit as st
from pathlib import Path

# Hardcoded path to the PDF file
pdf_path = Path("path/to/pdf/file.pdf")

# Streamlit app
def app():
    # Load the PDF file
    with pdf_path.open("rb") as f:
        pdf_bytes = f.read()

    # Show the PDF file in the Streamlit app
    st.write(pdf_bytes, format="pdf")

if __name__ == "__main__":
    app()