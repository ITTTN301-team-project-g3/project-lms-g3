from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Cho phép allowed_origins nhận cả chuỗi hoặc List
    allowed_origins: Union[List[str], str] = ["http://localhost:3000"]

    @field_validator("allowed_origins", mode="before")
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            # Tách chuỗi theo dấu phẩy thành List[str]
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Bỏ qua nếu có biến lạ/thừa trong .env
    )

settings = Settings()