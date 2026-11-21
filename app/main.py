from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.send import router as send_router
from app.simulator.probabilities import CHANNEL_PROBABILITIES
from datetime import datetime, timezone

app = FastAPI(
    title="Xeno Channel Service",
    description="Simulated messaging channel dispatcher — simulates WhatsApp, Email, and SMS delivery with async callbacks",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(send_router)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "xeno-channel-service",
        "version": "1.0.0",
        "supported_channels": sorted(list(CHANNEL_PROBABILITIES.keys())),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
