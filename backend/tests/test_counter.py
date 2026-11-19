"""Unit tests for the visitor counter. The database is mocked, so these run anywhere with no Azure access."""
import json
from unittest.mock import MagicMock

import pytest
from azure.core.exceptions import HttpResponseError, ResourceModifiedError, ResourceNotFoundError
from azure.data.tables import TableEntity

from counter import handle_request, increment_count


def make_entity(count):
    entity = TableEntity({"PartitionKey": "counter", "RowKey": "resume", "count": count})
    entity._metadata = {"etag": 'W/"etag-1"', "timestamp": None}
    return entity


@pytest.fixture
def table():
    return MagicMock()


def test_existing_count_goes_up_by_one(table):
    table.get_entity.return_value = make_entity(41)

    assert increment_count(table) == 42
    saved = table.update_entity.call_args.args[0]
    assert saved["count"] == 42


def test_first_visit_creates_the_counter(table):
    table.get_entity.side_effect = ResourceNotFoundError("missing")

    assert increment_count(table) == 1
    table.create_entity.assert_called_once()


def test_concurrent_update_is_retried(table):
    table.get_entity.side_effect = [make_entity(5), make_entity(6)]
    table.update_entity.side_effect = [ResourceModifiedError("changed"), None]

    assert increment_count(table) == 7
    assert table.update_entity.call_count == 2


def test_happy_path_returns_json_count(table):
    table.get_entity.return_value = make_entity(9)

    resp = handle_request(table)

    assert resp.status_code == 200
    assert resp.mimetype == "application/json"
    assert json.loads(resp.get_body()) == {"count": 10}


def test_database_error_returns_500(table):
    table.get_entity.side_effect = HttpResponseError("Cosmos DB unavailable")

    resp = handle_request(table)

    assert resp.status_code == 500
    assert json.loads(resp.get_body()) == {"error": "Could not update the visitor count"}
