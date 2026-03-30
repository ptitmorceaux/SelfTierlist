import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.config import SECRET_KEY, ALGO

def generate_jwt(user: dict, jwt_expir) -> str:
    payload = {
        "sub": str(user["id"]),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=int(jwt_expir)),
        "data": {
            "username": user["username"]
        }
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def verify_jwt(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# --- FastAPI dependency ---
bearer_scheme = HTTPBearer()

async def jwt_required(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    token = credentials.credentials
    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"user_id": int(payload["sub"]), "username": payload["data"]["username"]}
