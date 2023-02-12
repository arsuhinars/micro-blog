from pydantic import BaseSettings


class AppSettings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str

    class Config:
        secrets_dir = "/run/secrets"
