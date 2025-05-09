from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class SecretKeys(BaseSettings):
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = ""
    AWS_S3_BUCKET: str = ""
    AWS_S3_KEY: str = ""
    AWS_S3_PROCESSED_VIDEOS_BUCKET: str = ""
