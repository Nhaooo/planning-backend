import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/planning_db")
    admin_pin: str = os.getenv("ADMIN_PIN", "1234")
    backup_secret: str = os.getenv("BACKUP_SECRET", "backup-secret-key")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()