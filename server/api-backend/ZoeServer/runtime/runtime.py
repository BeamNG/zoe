from fastapi import APIRouter, FastAPI

app = FastAPI()

router = APIRouter(
    prefix="/runtime",
    tags=["runtime"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)