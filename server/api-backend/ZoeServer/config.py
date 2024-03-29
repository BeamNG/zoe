from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    ldap_server: str = ''
    ldap_readonly_user: str = ''
    ldap_readonly_pass: str = ''
    db_url: str = 'sqlite:///./sql_app.db'

    class Config:
        env_file = ".env"


@lru_cache()
def getSettings():
    return Settings()
