from pydantic import BaseModel

class SVNRepo(BaseModel):
    name: str
    uuid: str

    class Config:
        orm_mode = True