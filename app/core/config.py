from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Forum Backend"
    API_V1_STR: str = "/api/v1"
    
    # Recommend generating one using: openssl rand -hex 32
    SECRET_KEY: str = "changethissecretkeyinproduction!!!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    MYSQL_URL: str
    
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:5173", "http://localhost:5173"]

    SUPER_ROOT_USERNAME: str = "super_root"
    SUPER_ROOT_EMAIL: str = "root@localhost"
    SUPER_ROOT_PASSWORD: str = "root123456"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="allow")

settings = Settings()
