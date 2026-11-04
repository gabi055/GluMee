
from firebase_admin import auth
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import app.firebase

bearer = HTTPBearer(auto_error=False)

def get_uid(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    """Verifica el token de Firebase y devuelve el uid del usuario."""
    if creds is None:
        raise HTTPException(status_code=401, detail="Token ausente")
    try:
        decoded = auth.verify_id_token(creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return decoded["uid"]