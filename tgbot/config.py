from pydantic_settings import BaseSettings, SettingsConfigDict


# Класс для доступа к переменным окружения
class Settings(BaseSettings):
    TOKEN: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str
    CATALOGUE_ID: str
    KEY: str
    R_PASSWORD: str

    model_config = SettingsConfigDict(env_file='/app/.env')


settings = Settings()
