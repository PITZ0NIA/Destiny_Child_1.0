from fastapi import FastAPI

from . import models
from .db import Base, engine
from .routers import auth_router, init, roster, session_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Destiny Child - local server")

app.include_router(init.router)
app.include_router(auth_router.router)
app.include_router(session_router.router)
app.include_router(roster.router)


@app.get("/")
def root():
    return {"status": "Destiny Child local server running"}
