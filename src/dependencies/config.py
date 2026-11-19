from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    admin_username: str
    admin_password: str

    origins: list[str]

    model_config = SettingsConfigDict(env_file=".env")
