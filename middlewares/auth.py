from fastapi.security import OAuth2PasswordBearer



def authToken(token: str) -> OAuth2PasswordBearer:
    return OAuth2PasswordBearer(tokenUrl=token)





