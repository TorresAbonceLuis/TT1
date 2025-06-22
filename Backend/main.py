from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Para CORS (comunicación front/backend)

app = FastAPI()

# Configurar CORS para permitir conexión desde tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambia "*" por tu URL de GitHub Pages
    allow_methods=["GET", "POST"],
)

@app.get("/")
def read_root():
    return {"message": "Hola desde FastAPI!"}

@app.get("/saludar")
def saludar(nombre: str):
    return {"mensaje": f"¡Hola, {nombre}!"}