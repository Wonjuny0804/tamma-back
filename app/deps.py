import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

# Decodes the Supabase JWT, returns the current user's UID
def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = creds.credentials
    secret = os.getenv("SUPABASE_JWT_SECRET")
    print(secret)
    if not secret:
        raise HTTPException(500, "Server misconfiguration: missing JWT secret")
    

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid auth token")