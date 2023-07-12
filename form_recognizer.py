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

cognitive_service = get_azure_env_var()["AZURE_FORMRECOGNIZER_SERVICE"].replace('"', "")
# tenant_id = get_azure_env_var()["AZURE_TENANT_ID"]
endpoint = f"https://{cognitive_service}.cognitiveservices.azure.com/"
default_creds = AzureDeveloperCliCredential()
formUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/contoso-allinone.jpg"


def object_to_dict(obj):
    if isinstance(obj, dict):
        return {k: object_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [object_to_dict(item) for item in obj]
    elif hasattr(obj, "__dict__"):
        return object_to_dict(obj.__dict__)
    else:
        return obj


def get_document_text(filename, output):
    page_map = []

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
    paragraphs_raw = form_recognizer_results.paragraph

    page_map = []
    for table in tables_raw:
        table_obj = object_to_dict(table)
        for cell in table.cells:
            cell_obj = object_to_dict(cell)
            cell_obj["type"] = "table_cell"
            cell_obj["parent_table"] = table_obj["bounding_regions"]
            page_map.append(cell_obj)

    for paragraph in paragraphs_raw:
        paragraph_obj = object_to_dict(paragraph)
        paragraph_obj["type"] = "paragraph"
        page_map.append(paragraph_obj)
    with open(output, "w") as f:
        f.write(json.dumps(page_map))


res = get_document_text(
    "data/tender_request_01.pdf", output="data_output/tender_request_01.json"
)
print(res)
