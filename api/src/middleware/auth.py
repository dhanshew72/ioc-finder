import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]

_google_request = google_requests.Request()


class GoogleAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Missing or invalid Authorization header"}, status_code=401)

        token = auth_header.removeprefix("Bearer ")
        try:
            claims = id_token.verify_oauth2_token(token, _google_request, GOOGLE_CLIENT_ID)
        except Exception:
            return JSONResponse({"detail": "Invalid or expired token"}, status_code=401)

        if claims.get("hd") and "gmail.com" not in claims.get("email", ""):
            return JSONResponse({"detail": "Only Gmail accounts are permitted"}, status_code=403)

        request.state.user = {
            "email": claims["email"],
            "name": claims.get("name"),
            "sub": claims["sub"],
        }
        return await call_next(request)
