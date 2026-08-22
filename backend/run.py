import uvicorn
try:
    from backend.config import settings
    app_target = "backend.main:app"
except ImportError:
    from config import settings
    app_target = "main:app"

if __name__ == "__main__":
    print("⚡ Starting VOLT-LOGIC FastAPI Backend...")
    print(f"📡 Serving on http://{settings.HOST}:{settings.PORT}")
    print(f"🔒 CORS allowed origins: {settings.CORS_ORIGINS}")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    uvicorn.run(app_target, host=settings.HOST, port=settings.PORT, reload=(settings.ENVIRONMENT == "development"))
