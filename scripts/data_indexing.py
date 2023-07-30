from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *


search_creds = AzureKeyCredential("")
searchservice = ""

index_client = SearchIndexClient(
    endpoint=f"https://{searchservice}.search.windows.net/", credential=search_creds
)

line_index = SearchIndex(
    name="line-index",
    fields=[
        SimpleField(name="id", type="Edm.String", key=True),
        SimpleField(name="page_height", type="Edm.Double"),
        SimpleField(name="page_width", type="Edm.Double"),
        SimpleField(name="page_number", type="Edm.Int32"),
        SimpleField(name="page_unit", type="Edm.String"),
        SearchableField(
            name="content", type="Edm.String", analyzer_name="en.microsoft"
        ),
        SimpleField(
            name="polygon",
            collection=True,
            type="Collection(Edm.Double)",
            fields=[],
        ),
    ],
)

page_index = SearchIndex(
    name="extraction-page",
    fields=[
        SimpleField(name="id", type="Edm.String", key=True),
        SimpleField(name="height", type="Edm.Double"),
        SimpleField(name="width", type="Edm.Double"),
        SimpleField(name="page_number", type="Edm.Int32"),
        SimpleField(name="unit", type="Edm.String"),
        ComplexField(
            name="lines",
            collection=True,
            fields=[
                SearchableField(
                    name="content", type="Edm.String", analyzer_name="en.microsoft"
                ),
                ComplexField(
                    name="polygon",
                    collection=True,
                    type="Collection(Edm.String)",
                    fields=[SimpleField(name="value", type="Edm.String")],
                ),
            ],
        ),
    ],
)

table_index = SearchIndex(
    name="extraction-table",
    fields=[
        SimpleField(name="id", type="Edm.String", key=True),
        SearchableField(
            name="cell_content",
            collection=True,
            type="Collection(Edm.String)",
            analyer_name="en.microsoft",
        ),
        SimpleField(name="page_number", type="Edm.Int32"),
        SimpleField(name="table_number", type="Edm.Int32"),
        SimpleField(
            name="polygon",
            collection=True,
            type="Collection(Edm.Double)",
            fields=[],
        ),
        SimpleField(name="table_html", type="Edm.String", analyzer_name="en.microsoft"),
    ],
)

backup = SearchIndex(
    name="backup",
    fields=[
        SimpleField(name="id", type="Edm.String", key=True),
        SearchableField(
            name="content", type="Edm.String", analyzer_name="en.microsoft"
        ),
        SimpleField(name="type", type="Edm.String", filterable=True, facetable=True),
        SimpleField(
            name="page_number",
            type="Edm.Int32",
            filterable=True,
            facetable=True,
        ),
        ComplexField(
            name="bounding_box",
            fields=[
                ComplexField(
                    name="top_left",
                    fields=[
                        SimpleField(name="x", type="Edm.Double"),
                        SimpleField(name="y", type="Edm.Double"),
                    ],
                ),
                ComplexField(
                    name="top_right",
                    fields=[
                        SimpleField(name="x", type="Edm.Double"),
                        SimpleField(name="y", type="Edm.Double"),
                    ],
                ),
                ComplexField(
                    name="bottom_right",
                    fields=[
                        SimpleField(name="x", type="Edm.Double"),
                        SimpleField(name="y", type="Edm.Double"),
                    ],
                ),
                ComplexField(
                    name="bottom_left",
                    fields=[
                        SimpleField(name="x", type="Edm.Double"),
                        SimpleField(name="y", type="Edm.Double"),
                    ],
                ),
            ],
        ),
    ],
)


def create_search_index(index):
    print(f"Creating search index '{index}'")
    if index not in index_client.list_index_names():
        index = table_index
        index_client.create_index(index)
    else:
        print(f"Search index {index} already exists")


def index_sections(index_name, sections):
    search_client = SearchClient(
        endpoint=f"https://{searchservice}.search.windows.net/",
        index_name=index_name,
        credential=search_creds,
    )
    i = 0
    batch = []
    for s in sections:
        batch.append(s)
        i += 1
        if i % 1000 == 0:
            results = search_client.upload_documents(documents=batch)
            succeeded = sum([1 for r in results if r.succeeded])

            print(f"\tIndexed {len(results)} sections, {succeeded} succeeded")
            batch = []

    if len(batch) > 0:
        results = search_client.upload_documents(documents=batch)
        succeeded = sum([1 for r in results if r.succeeded])

        print(f"\tIndexed {len(results)} sections, {succeeded} succeeded")


def create_sections(list_of_sections):
    for i, doc in enumerate(list_of_sections):
        yield {
            "id": f"{i}-{doc['page_number']}",
            "page_number": doc["page_number"],
            "polygon": doc["polygon"],
            "cell_content": doc["cell_content"],
            "table_number": doc["table_number"],
            "table_html": doc["table_html"],
        }


def process(file_path):
    import os
    import json

    index_name = (
        os.path.basename(file_path).lower().replace(".json", "").replace("_", "-")
    )
    index_name = "extraction-table"
    create_search_index(index_name)

    print(f"Processing {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = json.load(f)
        sections = create_sections(content)
        index_sections(index_name=index_name, sections=sections)


process("data_output/tender_request_01.pdf/extraction-table.json")
