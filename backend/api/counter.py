"""Visitor counter logic, kept separate from the Azure Functions wiring so it can be unit tested."""
import json
import logging

import azure.functions as func
from azure.core import MatchConditions
from azure.core.exceptions import ResourceModifiedError, ResourceNotFoundError
from azure.data.tables import TableClient, UpdateMode

PARTITION_KEY = "counter"
ROW_KEY = "resume"
MAX_RETRIES = 5


def increment_count(table: TableClient) -> int:
    """Add 1 to the stored count and return the new value.

    Uses the entity's ETag so two visitors arriving at the same moment can't
    overwrite each other's update (optimistic concurrency).
    """
    for _ in range(MAX_RETRIES):
        try:
            entity = table.get_entity(partition_key=PARTITION_KEY, row_key=ROW_KEY)
        except ResourceNotFoundError:
            # First visit ever: create the counter row.
            try:
                table.create_entity({"PartitionKey": PARTITION_KEY, "RowKey": ROW_KEY, "count": 1})
                return 1
            except Exception:  # someone else created it first; read it again
                continue

        entity["count"] = int(entity.get("count", 0)) + 1
        try:
            table.update_entity(
                entity,
                mode=UpdateMode.REPLACE,
                etag=entity.metadata["etag"],
                match_condition=MatchConditions.IfNotModified,
            )
            return entity["count"]
        except ResourceModifiedError:
            continue  # another request updated it in between; retry with the fresh value

    raise RuntimeError("Could not update the visitor count after several retries")


def handle_request(table: TableClient) -> func.HttpResponse:
    """Turn a counter update into an HTTP response the web page can read."""
    try:
        count = increment_count(table)
    except Exception:
        logging.exception("Visitor counter failed")
        return func.HttpResponse(
            json.dumps({"error": "Could not update the visitor count"}),
            status_code=500,
            mimetype="application/json",
        )
    return func.HttpResponse(json.dumps({"count": count}), status_code=200, mimetype="application/json")
