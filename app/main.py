from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.send import router as send_router

app = FastAPI(
    title="Xeno Channel Service",
    description="Stubbed messaging channel — simulates WhatsApp, Email, and SMS delivery with async callbacks",
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
    return {"status": "ok", "service": "xeno-channel-service"}
