from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env")
    
    ## llm
    openai_api_key: str | None = None
    LLM_MODEL:str | None = None
    EMBEDDING_MODEL:str | None = None

    # Auth
    SECRET_KEY : str | None = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int | None = None

    # Base de données
    # DATABASE_URL=sqlite:///./medmind.db
    
settings = Settings()
