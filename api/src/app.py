from fastapi import FastAPI
from routes.extract import router as extract_router
from middleware.auth import GoogleAuthMiddleware

app = FastAPI()

app.add_middleware(GoogleAuthMiddleware)

app.include_router(extract_router)
