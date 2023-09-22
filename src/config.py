import os
from pathlib import Path


# def get_postgres_uri():
#     host = os.environ.get("DB_HOST", "localhost")
#     port = 54321 if host == "localhost" else 5432
#     password = os.environ.get("DB_PASSWORD", "abc123")
#     user, db_name = "allocation", "allocation"
#     return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
#

def get_db_url():
    env = os.environ.get('env', 'local')
    db_type = os.environ.get('db_type', 'lite')
    if env == 'local' and db_type == 'lite':
        db_path = str(Path(__file__).parent.parent) + "/local/db/lite.db"
        if os.path.exists(db_path):
            os.remove(db_path)

        return 'sqlite:///' + db_path


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 80 if host == "localhost" else 80
    return f"http://{host}:{port}"
