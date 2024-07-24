import os
from pathlib import Path


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "postgres_db")
    port = 5432 if host == "postgres_db" else 5432
    user = os.environ.get("DB_USER", "root_user")
    password = os.environ.get("DB_PASSWORD", "root_pwd")
    db_name = "retail_db"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_db_url():
    test_env = os.environ.get('ENV', 'LOCAL').upper()

    if test_env == 'LOCAL':
        db_path = str(Path(__file__).parent.parent) + "/local/db/lite.db"
        if os.path.exists(db_path):
            os.remove(db_path)

        return 'sqlite:///' + db_path
    else:
        return get_postgres_uri()


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 80 if host == "localhost" else 80
    return f"http://{host}:{port}"
