from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth
from db.base import Base
from db.pgsdb import engine

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
def root():
    return {"message": "Hello World!"}

Base.metadata.create_all(bind=engine)