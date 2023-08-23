from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from core.config import session, engine
from api import users, tweets, media

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(tweets.router)
api_router.include_router(media.router)

app = FastAPI()

app.include_router(api_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Instrumentator().instrument(app).expose(app)
@app.get("/api/test")
def test_api():
    return {"result": "True"}


@app.on_event("shutdown")
async def shutdown():
    await session.close()
    await engine.dispose()
