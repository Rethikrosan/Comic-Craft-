from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.routes import router

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description="AI-powered comic story creator using Gemini and Hugging Face image generation.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return {"status": "no favicon"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
