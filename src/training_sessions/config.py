import os

def get_postgres_uri():
    host = os.environ.get("DB_HOST", "172.30.48.1")
    port = 34526 if host == "172.30.48.1" else 5432
    password = os.environ.get("DB_PASSWORD", "training")
    user, db_name = "training_session_user", "training_sessions_dev"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

def get_whatsapp_api_details():
    access_token = os.environ.get("ACCESS_TOKEN", "")
    api_version = os.environ.get("VERSION", "")
    app_secret = os.environ.get("APP_SECRET", "")
    phone_number_id = os.environ.get("PHONE_NUMBER_ID", "")
    verify_token = os.environ.get("VERIFY_TOKEN", "")

    return {"access_token":access_token,
            "api_version":api_version,
            "app_secret":app_secret,
            "phone_number_id":phone_number_id,
            "verify_token":verify_token}

def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5000 if host == "localhost" else 80
    return f"http://{host}:{port}"


