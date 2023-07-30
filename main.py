import streamlit as st
from pathlib import Path
import base64

# Hardcoded path to the PDF file
pdf_path = Path("data/tender_request_01.pdf")
st.set_page_config(
    layout="wide",
    page_title="PDF search assistant",
    page_icon="🔍",
    initial_sidebar_state="collapsed",
)
col1, col2 = st.columns([1, 1])


def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")

    # Embedding PDF in HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" height="475" width="500" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


def get_pdf_parts(file):
    return "hello"


from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *

search_creds = AzureKeyCredential("")
searchservice = ""

index_client = SearchIndexClient(
    endpoint=f"https://{searchservice}.search.windows.net/", credential=search_creds
)

index_endpoint = f"https://{searchservice}.search.windows.net/"

search_client = SearchClient(
    endpoint=index_endpoint, index_name="line-index", credential=search_creds
)

from utils import save_annotated_image

OUTPUT_FOLDER = "frontend/public/data_output/annotated/"
import os

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

import streamlit.components.v1 as components


# Streamlit app
def app():
    search_term = st.text_input("Search term", "")
    st.header(search_term)

    if search_term:
        if not search_term in os.listdir(OUTPUT_FOLDER):
            results = search_client.search(search_term)
            st.write("searching and annotating...")
            all_image_paths = []
            all_results = []
            for result in results:
                bounding_box = result["polygon"]
                new_storage_folder = Path(OUTPUT_FOLDER) / search_term
                os.makedirs(new_storage_folder, exist_ok=True)
                input_image_path = os.path.join(
                    "data_output/tender_request_01.pdf/images/",
                    f"{result['page_number']}.jpg",
                )
                all_results.append(result["content"])

                bounding_box = result["polygon"]
                output_annotation_storage = os.path.join(
                    new_storage_folder, f"{result['id']}.jpg"
                )

                page_height = result["page_height"]
                page_width = result["page_width"]

                all_image_paths.append(output_annotation_storage)

                save_annotated_image(
                    input_image_path,
                    bounding_box,
                    output_annotation_storage,
                    page_height=page_height,
                    page_width=page_width,
                )

        imageCarouselComponent = components.declare_component(
            "image-carousel-component", path="frontend/public"
        )

        all_images = os.listdir(OUTPUT_FOLDER + f"/{search_term}")
        all_images = [f"data_output/annotated/{search_term}/" + x for x in all_images]
        st.write("Found {} results".format(len(all_images)))

        selectedImageUrl = imageCarouselComponent(imageUrls=all_images, height=200)

        if selectedImageUrl is not None:
            st.image(selectedImageUrl)

        import openai
        import json

        st.write("provided context:", json.dumps(all_results, indent=2))
        st.write("Generating answer...")

        api_key = ""
        openai.api_key = api_key
        prompt = "User will ask queries to get values of a particular elevator configuration. Summarize all the sentences, words you get and give the answer. Give two answers. One short that is just the value and another one the logic on how you determined it."
        context = json.dumps(all_results)
        st.write(get_chat_reply(prompt, context))


def get_chat_reply(prompt, context):
    import openai

    payload = {
        "messages": [
            {"role": "system", "content": "/start"},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": context},
        ]
    }
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=payload["messages"], max_tokens=500
    )
    assistant_reply = response.choices[0].message.content
    return assistant_reply


if __name__ == "__main__":
    app()
