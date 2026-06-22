import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    """Central place for environment-backed application settings."""

    secret_key = os.getenv("SECRET_KEY")
    algorithm = "HS256"
    mongo_url = os.getenv("MONGO_URL")
    backend_url = os.getenv("BACKEND_URL", "")
    frontend_url = os.getenv("FRONTEND_URL", "")
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")


settings = Settings()
