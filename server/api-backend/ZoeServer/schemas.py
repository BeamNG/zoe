from pydantic import BaseModel

class Test(BaseModel):
    id: int
    unique_name: str

    class Config:
        orm_mode = True


