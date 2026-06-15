from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Investment Analyzer API",
    description="Sistema de predicción de inversiones con ML",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar el frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Investment Analyzer API",
        "status": "running",
        "endpoints": {
            "yesterday": "/api/yesterday",
            "tomorrow": "/api/tomorrow",
            "accuracy": "/api/accuracy",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2026-06-16"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
