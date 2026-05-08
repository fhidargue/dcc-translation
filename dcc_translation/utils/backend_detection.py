from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure

from dcc_translation.config.env import mongo_pipeline_uri


def mongo_available(timeout=1) -> bool:
    """
    Check if MongoDB is available by attempting to connect to the server and retrieve server information
    """

    try:
        MongoClient(
            mongo_pipeline_uri(),
            serverSelectionTimeoutMS=timeout * 1000,
        ).server_info()
        return True
    except (ServerSelectionTimeoutError, OperationFailure):
        return False


def select_registry_backend() -> str:
    """
    Select the appropiate registry backend based on which is available
    """

    if mongo_available():
        return "mongo"

    return "sqlite"
