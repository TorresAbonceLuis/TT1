from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configura CORS primero
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importa los routers después de crear la app
from routers import upload, instruments

app.include_router(upload.router, prefix="/api/v1")
app.include_router(instruments.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "API funcionando"}