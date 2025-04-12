from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

import cloudinary

from src.api.contacts import router as contacts_router
from src.api.users import router as users_router
from src.auth.router import router as auth_router
from src.conf.config import settings  # імпорт з .env

app = FastAPI(
    title="Phonebook REST API",
    description="Контактний застосунок з авторизацією, аватарками та пошуком",
    version="1.0.0",
)

# Rate limiter middleware
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # заміни * на продакшн-домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cloudinary конфігурація з .env
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

# Підключення роутерів
app.include_router(auth_router)
app.include_router(contacts_router)
app.include_router(users_router)
