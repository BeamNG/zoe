from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import ZoeServer.ldap

router = APIRouter(
    tags=["auth"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

# user auth
# TODO: FIXME: fix the token being an actual token with secruity and not the username....
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/oauth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = token
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/oauth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    userinfo = ZoeServer.ldap.authenticate(form_data.username, form_data.password)
    if userinfo:
        return {"access_token": userinfo['username'], "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Login invalid")

@router.get("/users/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    return current_user