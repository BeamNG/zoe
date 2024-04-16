from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class SVNSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding='utf-8',
        env_file=('.env', '.env.prod'),
        extra='ignore'
    )

    svn_readonly_user: str = ''
    svn_readonly_pass: str = ''
    svn_server_URL: str = 'http://svn.intranet.beamng.com/'


@lru_cache()
def getSVNSettings():
    return SVNSettings()
