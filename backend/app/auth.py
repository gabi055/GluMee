import os
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

if not firebase_admin._apps:
    cred = credentials.Certificate(os.environ["FIREBASE_CREDENTIALS"])
    firebase_admin.initialize_app(cred)

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