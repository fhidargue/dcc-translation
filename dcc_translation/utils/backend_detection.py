from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure

from dcc_translation.config.env import mongo_pipeline_uri


def mongo_available(timeout=1):
    try:
        MongoClient(
            mongo_pipeline_uri(),
            serverSelectionTimeoutMS=timeout * 1000,
        ).server_info()
        return True
    except (ServerSelectionTimeoutError, OperationFailure):
        return False


def select_registry_backend():
    if mongo_available():
        return "mongo"

    return "sqlite"
