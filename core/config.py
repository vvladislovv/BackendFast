"""Конфигурация приложения."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database
    database_url: str
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Telegram
    telegram_bot_token: str
    telegram_admin_ids: str
    
    # Email
    email_host: str = "smtp.beget.ru"
    email_port: int = 465
    email_user: str
    email_password: str
    email_from: str
    email_admin: str
    
    # Application
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    log_rotation: str = "10 MB"
    log_retention: str = "30 days"
    
    @property
    def admin_ids_list(self) -> list[int]:
        """Список ID администраторов Telegram."""
        return [int(id_) for id_ in self.telegram_admin_ids.split(",")]


settings = Settings()
