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

cognitive_service = get_azure_env_var()["AZURE_FORMRECOGNIZER_SERVICE"].replace('"', "")
# tenant_id = get_azure_env_var()["AZURE_TENANT_ID"]
endpoint = f"https://{cognitive_service}.cognitiveservices.azure.com/"
default_creds = AzureDeveloperCliCredential()
formUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/contoso-allinone.jpg"
document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=default_creds
)

poller = document_analysis_client.begin_analyze_document_from_url(
    "prebuilt-layout", formUrl
)
result = poller.result()
print(result)


# def format_pages(pages):
#     return pages


# def format_tables(tables):
#     return [
#         {"table_number": idx + 1, "content": table} for idx, table in enumerate(tables)
#     ]


# def format_paragraphs(paragraphs):
#     return paragraphs
