import os

def get_postgres_uri():
    host = os.environ.get("DB_HOST", "172.30.48.1")
    port = 34526 if host == "172.30.48.1" else 5432
    password = os.environ.get("DB_PASSWORD", "training")
    user, db_name = "training_session_user", "training_sessions_dev"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"



def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5000 if host == "localhost" else 80
    return f"http://{host}:{port}"


