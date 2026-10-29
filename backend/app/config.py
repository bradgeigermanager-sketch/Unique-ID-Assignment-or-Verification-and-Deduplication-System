python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j"
    database_url: str = "postgresql://user:pass@localhost/hr_db"
    file_upload_dir: str = "/tmp/org_files"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
