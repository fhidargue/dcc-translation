from dotenv import load_dotenv
import os

load_dotenv()


def get_env(name: str, default=None):
    return os.getenv(name, default)


# Mongo settings
MONGO_HOST = get_env("DCC_MONGO_HOST", "localhost")
MONGO_PORT = int(get_env("DCC_MONGO_PORT", 27017))
MONGO_DB = get_env("DCC_MONGO_DB", "dcc_translation")

MONGO_ADMIN_USER = get_env("DCC_MONGO_ADMIN_USER", "admin")
MONGO_ADMIN_PASS = get_env("DCC_MONGO_ADMIN_PASS", "adminpass")

MONGO_PIPELINE_USER = get_env("DCC_MONGO_PIPELINE_USER", "pipeline_user")
MONGO_PIPELINE_PASS = get_env("DCC_MONGO_PIPELINE_PASS", "pipeline_pass")

SQLITE_PATH = get_env("DCC_SQLITE_PATH", None)


def mongo_admin_uri() -> str:
    return (
        f"mongodb://{MONGO_ADMIN_USER}:{MONGO_ADMIN_PASS}"
        f"@{MONGO_HOST}:{MONGO_PORT}/admin"
    )


def mongo_pipeline_uri() -> str:
    return (
        f"mongodb://{MONGO_PIPELINE_USER}:{MONGO_PIPELINE_PASS}"
        f"@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
        f"?authSource={MONGO_DB}"
    )
