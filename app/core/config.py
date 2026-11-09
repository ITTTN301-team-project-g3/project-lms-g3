<<<<<<< HEAD
from typing import Union, List
=======
from typing import List, Union
>>>>>>> 3bd636b87ae0cb6dfb3c03a923f32bf8b64e60ba
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
<<<<<<< HEAD
    allowed_origins: Union[List[str], str] = ["http://localhost:3000"]

    @field_validator("allowed_origins", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
=======
    
    # Cho phép allowed_origins nhận cả chuỗi hoặc List
    allowed_origins: Union[List[str], str] = ["http://localhost:3000"]

    @field_validator("allowed_origins", mode="before")
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            # Tách chuỗi theo dấu phẩy thành List[str]
            return [i.strip() for i in v.split(",") if i.strip()]
        return v
>>>>>>> 3bd636b87ae0cb6dfb3c03a923f32bf8b64e60ba

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
<<<<<<< HEAD
        extra="ignore"
=======
        extra="ignore"  # Bỏ qua nếu có biến lạ/thừa trong .env
>>>>>>> 3bd636b87ae0cb6dfb3c03a923f32bf8b64e60ba
    )

settings = Settings()