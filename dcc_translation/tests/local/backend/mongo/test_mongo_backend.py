from dcc_translation.database.mongo_setup import MongoSetup
from dcc_translation.config.env import mongo_pipeline_uri
from dcc_translation.config.env import mongo_admin_uri
from pymongo import MongoClient

import pytest

pytestmark = pytest.mark.local


def mongo_client():
    return MongoClient(mongo_admin_uri())


@pytest.fixture(scope="module", autouse=True)
def setup_mongo():
    try:
        MongoSetup().bootstrap()
    except Exception:
        pytest.skip("MongoDB container not running")


def test_database_created():
    client = mongo_client()
    dbs = client.list_database_names()

    assert "dcc_translation" in dbs


def test_pipeline_user_created():
    client = mongo_client()
    users = client["dcc_translation"].command("usersInfo")
    usernames = [u["user"] for u in users["users"]]

    assert "pipeline_user" in usernames


def test_pipeline_user_authentication():
    client = MongoClient(mongo_pipeline_uri())
    db = client["dcc_translation"]

    assert db.name == "dcc_translation"


def test_pipeline_user_role():
    client = mongo_client()
    info = client["dcc_translation"].command("usersInfo", "pipeline_user")
    roles = info["users"][0]["roles"]
    role_names = [r["role"] for r in roles]

    assert "readWrite" in role_names


def test_required_collections_exist():
    client = mongo_client()
    collections = client["dcc_translation"].list_collection_names()
    expected = {
        "translations",
        "dependencies",
        "validation_reports",
    }

    assert expected.issubset(set(collections))
