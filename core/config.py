from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore') # Added extra='ignore' for flexibility

    # Security settings
    secret_key: str = "my-secure-dev-key" # IMPORTANT: CHANGE THIS IN PRODUCTION!
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database settings (if you need to externalize this later)
    # sqlalchemy_database_url: str = "sqlite:///./sql_app.db"

    # --- AI Specific Settings ---
    openai_api_key: Optional[str] = None # Your OpenAI API key
    ai_model_name: str = "gpt-4o" # Default LLM model to use
    
    # You might add more specific settings for embedding models or other AI services here
    # For example, if you switch to a hosted embedding service:
    # embedding_model_provider: str = "SentenceTransformers"
    # embedding_model_name: str = "all-MiniLM-L6-v2"

settings = Settings()
