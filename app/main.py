from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.services.limiter import limiter 

from routes import auth, contacts, users


app = FastAPI(
    title="Contacts API",
    description="REST API for managing contacts with authentication",
    version="1.0.0",
)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )


app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/")
async def root():
    return {"message": "API is working"}


@app.get("/health")
async def health():
    return {"status": "ok"}