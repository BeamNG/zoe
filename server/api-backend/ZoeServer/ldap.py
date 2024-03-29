from fastapi import Depends, APIRouter, HTTPException
import ldap3

from ZoeServer.config import Settings, getSettings

router = APIRouter(
    prefix="/ldap",
    tags=["ldap"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

def available():
    return getSettings().ldap_server

def _getLdapUserInfo(conn, username):
    groups = []
    displayName = ''
    # look for full name
    if conn.search('ou=users,dc=beamng,dc=com', '(cn={})'.format(username), attributes='*'):
        if len(conn.response) > 0:
            attr = conn.response[0]['attributes']
            displayName = '{} {}'.format(attr['givenName'][0], attr['sn'][0])
    else:
        raise HTTPException(status_code=404, detail="User not found")
    # then look for the groups the user has
    if conn.search('ou=groups,dc=beamng,dc=com', '(&(objectClass=posixGroup)(memberUid={}))'.format(username), attributes='cn'):
        for e in conn.response:
            groups.append(e['attributes']['cn'][0])
    # return everything
    return {
        'username': username,
        'displayName': displayName,
        'email': '{}@beamng.com'.format(username),
        'groups': groups
    }

def authenticate(username, password, settings):
    try:
        server = ldap3.Server(settings.ldap_server)
        with ldap3.Connection(server, 'cn={},ou=users,dc=beamng,dc=com'.format(username), password, auto_bind=True) as conn:
            return _getLdapUserInfo(conn, username)
    except Exception as e:
        raise HTTPException(status_code=403, detail="Login invalid")

@router.get("/authenticate/{username}/{password}", tags=["ldap"])
def read_item(username: str, password: str):
    # disabled for now
    if True:
        raise HTTPException(status_code=403)
    return authenticate(username, password, settings)

@router.get("/user/{username}", tags=["ldap"])
def read_item(username: str, settings: Settings = Depends(getSettings)):
    server = ldap3.Server(settings.ldap_server)
    with ldap3.Connection(server, settings.ldap_readonly_user, settings.ldap_readonly_pass, auto_bind=True) as conn:
        return _getLdapUserInfo(conn, username)

@router.get("/users", tags=["ldap"])
def read_item(settings: Settings = Depends(getSettings)):
    server = ldap3.Server(settings.ldap_server)
    users = []
    with ldap3.Connection(server, settings.ldap_readonly_user, settings.ldap_readonly_pass, auto_bind=True) as conn:
        if conn.search('ou=users,dc=beamng,dc=com', '(objectClass=posixAccount)', attributes='cn'):
            for e in conn.response:
                users.append(e['attributes']['cn'][0])
    return users

@router.get("/group/{group_name}/users", tags=["ldap"])
def read_item(group_name: str, settings: Settings = Depends(getSettings)):
    server = ldap3.Server(settings.ldap_server)
    users = []
    with ldap3.Connection(server, settings.ldap_readonly_user, settings.ldap_readonly_pass, auto_bind=True) as conn:
        if conn.search('ou=groups,dc=beamng,dc=com', '(&(objectClass=posixGroup)(cn={}))'.format(group_name), attributes='memberUid'):
            if len(conn.response) > 0:
                for e in conn.response[0]['attributes']['memberUid']:
                    users.append(e)
        else:
            raise HTTPException(status_code=404, detail="Group not found")
    return users

@router.get("/groups", tags=["ldap"])
def read_item(settings: Settings = Depends(getSettings)):
    server = ldap3.Server(settings.ldap_server)
    groups = []
    with ldap3.Connection(server, settings.ldap_readonly_user, settings.ldap_readonly_pass, auto_bind=True) as conn:
        if conn.search('ou=groups,dc=beamng,dc=com', '(objectClass=posixGroup)', attributes='cn'):
            for e in conn.response:
                groups.append(e['attributes']['cn'][0])
    return groups

