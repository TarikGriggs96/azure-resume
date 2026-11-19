"""Azure Functions entry point (Python v2 programming model)."""
import os
import logging


logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)


import azure.functions as func
from azure.data.tables import TableClient

from counter import handle_request

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def get_table() -> TableClient:
    # The connection string comes from app settings (local.settings.json locally,
    # Function App configuration in Azure). It is never written in code.
    return TableClient.from_connection_string(
        conn_str=os.environ["COSMOS_CONNECTION_STRING"],
        table_name=os.environ.get("COSMOS_TABLE_NAME", "visitors"),
    )


@app.route(route="visitors", methods=["GET", "POST"])
def visitors(req: func.HttpRequest) -> func.HttpResponse:
    return handle_request(get_table())
