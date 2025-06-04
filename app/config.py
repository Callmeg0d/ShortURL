from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_URL(self):
        return (f'postgresql+asyncpg://{self.DB_USER}:'
                f'{self.DB_PASSWORD}@{self.DB_HOST}:'
                f'{self.DB_PORT}/{self.DB_NAME}')

    model_config = SettingsConfigDict(env_file=env_path)

settings = Settings()
