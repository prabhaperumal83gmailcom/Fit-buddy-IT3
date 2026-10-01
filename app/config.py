from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = 'FitBuddy'
    debug: bool = True
    database_url: str = 'sqlite:///./fitbuddy.db'
    gemini_api_key: str = ''
    gemini_model: str = 'gemini-3.8-flash'
    gemini_fallback_models: str = 'gemini-3.7-flash'
    admin_key: str = 'change-me'
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False, extra='ignore')
    @property
    def fallback_models(self):
        return [x.strip() for x in self.gemini_fallback_models.split(',') if x.strip()]

@lru_cache
def get_settings():
    return Settings()
settings = get_settings()
