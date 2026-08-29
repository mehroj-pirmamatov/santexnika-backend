from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import categories, products
from app.routers import categories, products, orders
from fastapi.middleware.cors import CORSMiddleware
from app.routers import categories, products, orders, auth,users

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="A1 Santexnika API", lifespan=lifespan)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(auth.router)
app.include_router(auth.router)
app.include_router(users.router)

import os
from fastapi.staticfiles import StaticFiles

# Static papkani yaratish va ulash
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "A1 Santexnika backend ishlayapti!"}


