from pydantic import BaseSettings
from functools import lru_cache

class SVNSettings(BaseSettings):
    svn_readonly_user: str = ''
    svn_readonly_pass: str = ''
    svn_server_URL: str = 'http://svn.intranet.beamng.com/'

    class Config:
        env_file = ".env"

@lru_cache()
def getSVNSettings():
    return SVNSettings()
