from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CRM_RECEIPT_URL: str = "http://localhost:8000/api/receipts"
    PORT: int = 8001

    class Config:
        env_file = ".env"

settings = Settings()
print(f"[CHANNEL SERVICE] CRM_RECEIPT_URL = {settings.CRM_RECEIPT_URL}")
