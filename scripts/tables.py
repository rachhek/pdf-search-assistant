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

index_name = "extraction-table"

search_client = SearchClient(
    endpoint=index_endpoint, index_name="extraction-table", credential=search_creds
)

from utils import save_annotated_image

OUTPUT_FOLDER = "frontend/public/data_output/annotated/"
import os

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

import streamlit.components.v1 as components
import json
import openai

api_key = ""
openai.api_key = api_key

answer_map = []


def get_summary_text(text):
    st.write("Summarizing all the findings from above: ")
    prompt = f"Summarize the findings from above: {text}. Group them per category you find. Try to mention the how many times you found the same category and answer. \
    Ask for clarification if you need more. Be transparent about your confusion and encourage user to refer to the drawings."
    reply = get_chat_reply(prompt, text)
    return reply


def get_openai_answer(search_term, context):
    st.write(f"Reading the table on the left for {search_term}...")
    prompt = f"Is there a {search_term} mentioned here? What is the {search_term}? Please be very specific and search for exact matches.\
    Here is some training example and answer in the same way:\
    Tabel cell: \
    Info: Shaft Size (W mm x D mm)	10850mm W x 2500 mm D -combined shaft for 4 lifts -Refer to drawings \
    Answer: It means shaft Width=10850mm and shaft Depth=2500mm. Extra notes is to refer to drawings combined shaft for 4 lifts \
    \
    Table Cell:\
    Info: Car Size (W mm x D mm x H mm)	1900 x 1500 x 2600 (under decorative ceiling)\
    Answer: Car width = 1900mm, car depth == 1500mm and car height ==2600mm \
    \
    If you don't find it look for it again and confirm again.\
    The {search_term} is linked to a particular elevator reference. Please mention the elevator referenced for this.\
    An example of elevator references is PL1, PL2, PL3, PL4, Passenger Elevators for Tower 3 (Low Zone), EAST TOWER, LOW ZONE PASSENGER LIFTS.\
    "
    reply = get_chat_reply(prompt, context)
    return reply


def search_results(search_term):
    results = search_client.search(search_term)
    return results


def print_table(idx, result, search_term):
    col1, col2 = st.columns([1, 1])
    header_desc = f"Result #{idx} ---from page {result['page_number']}----table {result['table_number']}"
    st.header(header_desc)
    with col1:
        st.markdown(result["table_html"], unsafe_allow_html=True)
    with col2:
        reply = get_openai_answer(search_term, result["table_html"])
        answer_map.append({"page": result["page_number"], reply: reply})
        st.markdown(reply, unsafe_allow_html=True)


# Streamlit app
def app():
    st.header("Extract Tables and answer questions")
    search_term = st.text_input("Search term", "")

    st.header(search_term)

    if search_term:
        results = search_results(search_term)
        st.write("searching and annotating...")
        all_image_paths = []
        all_results = []
        for idx, result in enumerate(results):
            print_table(idx, result, search_term)

            bounding_box = result["polygon"]
            new_storage_folder = Path(OUTPUT_FOLDER) / search_term
            os.makedirs(new_storage_folder, exist_ok=True)
            input_image_path = os.path.join(
                "data_output/tender_request_01.pdf/images/",
                f"{result['page_number']}.jpg",
            )
            all_results.append(result["table_html"])

            bounding_box = result["polygon"]
            output_annotation_storage = os.path.join(
                new_storage_folder, f"{result['id']}.jpg"
            )

            page_height = 8.2639
            page_width = 11.6806

            all_image_paths.append(output_annotation_storage)

            save_annotated_image(
                input_image_path,
                bounding_box,
                output_annotation_storage,
                page_height=page_height,
                page_width=page_width,
            )

        st.header("Summarizing all answers: ")
        summary_reply = get_summary_text(str(answer_map))
        st.write(summary_reply)

        imageCarouselComponent = components.declare_component(
            "image-carousel-component", path="frontend/public"
        )

        all_images = os.listdir(OUTPUT_FOLDER + f"/{search_term}")
        all_images = [f"data_output/annotated/{search_term}/" + x for x in all_images]
        st.write("Found {} results".format(len(all_images)))

        selectedImageUrl = imageCarouselComponent(imageUrls=all_images, height=200)

        if selectedImageUrl is not None:
            st.image(selectedImageUrl)

        # st.write("provided context:", json.dumps(all_results, indent=2))
        # st.write("Generating answer...")

        # api_key = ""
        # openai.api_key = api_key
        # prompt = f"Is there a {search_term} mentioned here? What is the {search_term}?"
        # context = json.dumps(all_results)
        # st.write(get_chat_reply(prompt, context))


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
