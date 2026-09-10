from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Task Management & Productivity Analytics Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql+psycopg://postgres@localhost:5432/task_productivity"
    TEST_DATABASE_URL: str = "postgresql+psycopg://postgres@localhost:5432/task_productivity_test"

    # JWT Settings
    JWT_SECRET_KEY: str = "dev_secret_key_change_in_production_1234567890_super_secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
