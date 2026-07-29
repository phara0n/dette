import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routes import compensations, dashboard, friends, purchases, repayments

Base.metadata.create_all(bind=engine)

root_path = os.getenv("ROOT_PATH", "")

app = FastAPI(title="Dette - Gestion de dettes", root_path=root_path)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(friends.router)
app.include_router(purchases.router)
app.include_router(repayments.router)
app.include_router(compensations.router)
app.include_router(dashboard.router)
