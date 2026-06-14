from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CRM_RECEIPT_URL: str = "https://xeno-crm-ry0s.onrender.com/api/receipts"
    PORT: int = 8001

    class Config:
        env_file = ".env"

settings = Settings()
print(f"[CHANNEL SERVICE] CRM_RECEIPT_URL = {settings.CRM_RECEIPT_URL}")
