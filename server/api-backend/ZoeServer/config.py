from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding='utf-8',
        env_file=('.env', '.env.prod'),
        extra='ignore'
    )

    ldap_server: str = ''
    ldap_readonly_user: str = ''
    ldap_readonly_pass: str = ''
    db_url: str = 'sqlite:///./sql_app.db'

@lru_cache()
def getSettings():
    return Settings()
