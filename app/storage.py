import json
import logging

import boto3
from botocore.config import Config
import certifi
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)

_client = None

class S3ClientProvider:
    """
    Provides a singleton S3 client instance and utility methods
    for storing and loading article content and documents.
    """

    _client = None

    @classmethod
    def _s3_configured(cls) -> bool:
        return bool(settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY)  

    @classmethod
    def get_client(cls):
        if cls._client is None and cls._s3_configured():
            config = Config(
                retries={
                    "max_attempts": 5,
                    "mode": "standard"
                }
            )
            cls._client = boto3.client(
                "s3",
                region_name=settings.S3_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                verify=certifi.where(),
                config=config
            )
        return cls._client
    
    @classmethod
    def store_article_json(cls, article_id: str, content: str) -> str:
        content_key = f"articles/{article_id}"

        if not cls._s3_configured():
            logger.warning("S3 not configured, skipping content upload for %s", article_id)
            return content_key
        
        client = cls.get_client()

        if client:
            client.put_object(
                Bucket=settings.S3_BUCKET,
                Key=f"{content_key}/content.json",
                Body=content.encode(),
                ContentType="application/json",
            )

        return content_key
    
    @classmethod
    def store_article_bin(cls, article_id: str, binary: bytes) -> str:
        document_key = f"articles/{article_id}"

        if not cls._s3_configured():
            logger.warning("S3 not configured, skipping document upload for %s", article_id)
            return document_key
        
        client = cls.get_client()

        if client:
            client.put_object(
                Bucket=settings.S3_BUCKET,
                Key=f"{document_key}/document.bin",
                Body=binary,
                ContentType="application/octet-stream",
            )

        return document_key

    @classmethod
    def load_article_json(cls, article_id: str) -> dict | None:
        if not cls._s3_configured():
            return None
        try:
            client = cls.get_client()
            if client:
                response = client.get_object(
                    Bucket=settings.S3_BUCKET,
                    Key=f"articles/{article_id}/content.json",
                )
                return json.loads(response["Body"].read())
        except ClientError as e:
            if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
                return None
            raise

    @classmethod
    def load_article_bin(cls, article_id: str) -> bytes | None:
        if not cls._s3_configured():
            return None
        try:
            client = cls.get_client()
            if client:
                response = client.get_object(
                    Bucket=settings.S3_BUCKET,
                    Key=f"articles/{article_id}/document.bin",
                )
                return response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
                return None
            raise
