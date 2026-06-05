import base64
import logging

import boto3
import certifi

from app.config import settings

logger = logging.getLogger(__name__)

_client = None


def _s3_configured() -> bool:
    return bool(settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY)


def get_s3():
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            region_name=settings.S3_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            verify=certifi.where(),
        )
    return _client


def store_article(article_id: str, content_json: str, ydoc_state_b64: str) -> str:
    content_key = f"articles/{article_id}"

    if not _s3_configured():
        logger.warning("S3 not configured, skipping upload for %s", article_id)
        return content_key

    s3 = get_s3()
    s3.put_object(
        Bucket=settings.S3_BUCKET,
        Key=f"{content_key}/content.json",
        Body=content_json.encode(),
        ContentType="application/json",
    )
    s3.put_object(
        Bucket=settings.S3_BUCKET,
        Key=f"{content_key}/document.bin",
        Body=base64.b64decode(ydoc_state_b64),
        ContentType="application/octet-stream",
    )

    return content_key
