"""
This code sample shows Prebuilt Layout operations with the Azure Form Recognizer client library. 
The async versions of the samples require Python 3.6 or later.

To learn more, please visit the documentation - Quickstart: Form Recognizer Python client library SDKs
https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/quickstarts/try-v3-python-sdk
"""

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.identity import AzureDeveloperCliCredential
from azure.core.credentials import AzureKeyCredential

from utils import get_azure_env_var
import json
import html


from io import BytesIO
import os
import PyPDF2
from PIL import Image

cognitive_service = get_azure_env_var()["AZURE_FORMRECOGNIZER_SERVICE"].replace('"', "")
# tenant_id = get_azure_env_var()["AZURE_TENANT_ID"]
endpoint = f"https://{cognitive_service}.cognitiveservices.azure.com/"
default_creds = AzureDeveloperCliCredential()
formUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/contoso-allinone.jpg"


def convert_polygons_to_list(polygons_data):
    return [item for sublist in polygons_data for item in sublist]


def object_to_dict(obj):
    if isinstance(obj, dict):
        return {k: object_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [object_to_dict(item) for item in obj]
    elif hasattr(obj, "__dict__"):
        return object_to_dict(obj.__dict__)
    else:
        return obj


def table_to_html(table):
    table_html = "<table>"
    rows = [
        sorted(
            [cell for cell in table.cells if cell.row_index == i],
            key=lambda cell: cell.column_index,
        )
        for i in range(table.row_count)
    ]
    for row_cells in rows:
        table_html += "<tr>"
        for cell in row_cells:
            tag = (
                "th"
                if (cell.kind == "columnHeader" or cell.kind == "rowHeader")
                else "td"
            )
            cell_spans = ""
            if cell.column_span > 1:
                cell_spans += f" colSpan={cell.column_span}"
            if cell.row_span > 1:
                cell_spans += f" rowSpan={cell.row_span}"
            table_html += f"<{tag}{cell_spans}>{html.escape(cell.content)}</{tag}>"
        table_html += "</tr>"
    table_html += "</table>"
    return table_html


def get_document_text(filename, output):
    page_map = []
    table_map = []
    paragraph_map = []

    print(f"Extracting text from '{filename}' using Azure Form Recognizer")
    form_recognizer_client = DocumentAnalysisClient(
        endpoint=endpoint,
        credential=default_creds,
        headers={"x-ms-useragent": "azure-search-chat-demo/1.0.0"},
    )
    with open(filename, "rb") as f:
        poller = form_recognizer_client.begin_analyze_document(
            "prebuilt-layout", document=f
        )
        form_recognizer_results = poller.result()

    # for tables and paragraphs in the document (including headers and footers)
    tables_raw = form_recognizer_results.tables
    paragraphs_raw = form_recognizer_results.paragraphs
    pages_raw = form_recognizer_results.pages

    for idx, table in enumerate(tables_raw):
        table_obj = object_to_dict(table)

        table_obj = {}
        table_obj["polygon"] = convert_polygons_to_list(
            object_to_dict(table.bounding_regions[0].polygon)
        )
        table_obj["page_number"] = table.bounding_regions[0].page_number
        table_obj["cell_content"] = [
            cell.content for cell in table.cells if cell.content != ""
        ]
        table_obj["table_number"] = idx
        table_obj["table_html"] = table_to_html(table)
        # for cell in table.cells:
        #     cell_obj = object_to_dict(cell)
        #     cell_obj["type"] = "table_cell"
        #     cell_obj["parent_table_polygon"] = table_obj["bounding_regions"][0]["polygon"]
        #     cell_obj["page_number"] = table_obj["bounding_regions"][0]["page_number"]
        #     page_map.append(cell_obj)
        table_map.append(table_obj)

    for paragraph in paragraphs_raw:
        paragraph_obj = object_to_dict(paragraph)
        paragraph_obj["type"] = "paragraph"

        paragraph_obj["bounding_box"] = {}
        paragraph_obj["bounding_box"]["top_left"] = {}
        paragraph_obj["bounding_box"]["top_left"]["x"] = paragraph_obj[
            "bounding_regions"
        ][0]["polygon"][0][0]
        paragraph_obj["bounding_box"]["top_left"]["y"] = paragraph_obj[
            "bounding_regions"
        ][0]["polygon"][0][1]

        paragraph_obj["bounding_box"]["top_right"] = {}
        paragraph_obj["bounding_box"]["top_right"]["x"] = paragraph_obj[
            "bounding_regions"
        ][0]["polygon"][1][0]
        paragraph_obj["bounding_box"]["top_right"]["y"] = paragraph_obj[
            "bounding_regions"
        ][0]["polygon"][1][1]

        paragraph_obj["bounding_box"]["bottom_right"] = {}
        paragraph_obj["bounding_box"]["bottom_right"]["x"] = paragraph_obj[
            "bounding_regions"
        ][0]["polygon"][2][0]
        paragraph_obj["bounding_box"]["bottom_right"]["y"] = paragraph_obj[
            "bounding_regions"
        ][0]["polygon"][2][1]

        paragraph_obj["bounding_box"]["bottom_left"] = {}
        paragraph_obj["bounding_box"]["bottom_left"]["x"] = paragraph_obj[
            "bounding_regions"
        ][0]["polygon"][3][0]
        paragraph_obj["bounding_box"]["bottom_left"]["y"] = paragraph_obj[
            "bounding_regions"
        ][0]["polygon"][3][1]

        paragraph_obj["page_number"] = paragraph_obj["bounding_regions"][0][
            "page_number"
        ]
        paragraph_map.append(paragraph_obj)

    for page in pages_raw:
        for line in page.lines:
            line_obj = {}
            line_obj["page_number"] = page.page_number
            line_obj["page_height"] = page.height
            line_obj["page_width"] = page.width
            line_obj["page_unit"] = page.unit
            line_obj["content"] = line.content
            line_obj["polygon"] = convert_polygons_to_list(object_to_dict(line.polygon))
            page_map.append(line_obj)

    with open(output + "-page.json", "w") as f:
        f.write(json.dumps(page_map))

    with open(output + "-table.json", "w") as f:
        f.write(json.dumps(table_map))

    with open(output + "-paragraph.json", "w") as f:
        f.write(json.dumps(paragraph_map))


# FILL THIS file
input_file_path = "data/tender_request_01.pdf"
output_folder = "data_output"

# Create a folder for the output
file_name = os.path.basename(input_file_path)
file_output_folder = os.path.join(output_folder, file_name)
images_output_folder = os.path.join(file_output_folder, "images")
os.makedirs(file_output_folder, exist_ok=True)
os.makedirs(images_output_folder, exist_ok=True)

get_document_text(input_file_path, output=f"{file_output_folder}/extraction")

# import module
from pdf2image import convert_from_path


# # Store Pdf with convert_from_path function
# images = convert_from_path(input_file_path, dpi=250)

# for i in range(len(images)):
#     # Save pages as images in the pdf
#     images[i].save(f"{images_output_folder}/" + str(i + 1) + ".jpg", "JPEG")
