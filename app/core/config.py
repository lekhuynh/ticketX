from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # user: str
    # password: str
    # host: str
    # port: str
    # dbname: str
    ALEMBIC_DB_URL: str
    DATABASE_URL: str
    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    GOOGLE_API_KEY: str
    # VNPay
    vnp_TmnCode: str
    vnp_HashSecret: str
    vnp_Url: str
    VNPAY_RETURN_URL: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()