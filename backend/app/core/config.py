import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Configuration model to load environment vars
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DATABASE_URL: str = Field(
        default="postgresql://postgres:password123@localhost:5432/impactgraph"
    )
    
    JWT_SECRET: str = Field(
        default="6027c62d007d4b4e8e5cf3bb5f2940cbafaad522b045e821614623b2b7f2940c"
    )
    
    JWT_ALGORITHM: str = Field(default="HS256")
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440) # 24 hours
    
    IMPACTGRAPH_SECRET_KEY: str = Field(
        default="9899aa320bff4125aad8d365b6077ad59899aa320bff4125aad8d365b6077ad5"
    )

    @property
    def clean_database_url(self) -> str:
        # Standardize PostgreSQL URLs for SQLAlchemy (e.g. replacing postgres:// with postgresql:// if needed)
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL

# Global configuration instance
settings = Settings()
