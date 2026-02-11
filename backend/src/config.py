"""
Configuration — Cross-Border Payment Intelligence Platform
"""
from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://xborder:xborder123@localhost:5432/xborder"
    )

    # Auth
    jwt_secret: str = Field(default="dev-secret-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Environment
    environment: Literal["development", "production"] = "development"

    # LLM (optional — product works without it, LLM enhances explanations)
    llm_provider: Literal["none", "openai", "groq", "ollama"] = "none"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-70b-versatile"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
