import json
import logging

import boto3
import certifi
from botocore.exceptions import ClientError

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


def store_article_content(article_id: str, content_json: str) -> str:
    content_key = f"articles/{article_id}"

    if not _s3_configured():
        logger.warning("S3 not configured, skipping content upload for %s", article_id)
        return content_key

    get_s3().put_object(
        Bucket=settings.S3_BUCKET,
        Key=f"{content_key}/content.json",
        Body=content_json.encode(),
        ContentType="application/json",
    )

    return content_key


def store_document(article_id: str, binary: bytes) -> None:
    if not _s3_configured():
        logger.warning("S3 not configured, skipping document upload for %s", article_id)
        return

    get_s3().put_object(
        Bucket=settings.S3_BUCKET,
        Key=f"articles/{article_id}/document.bin",
        Body=binary,
        ContentType="application/octet-stream",
    )


def load_article_content(article_id: str) -> dict | None:
    if not _s3_configured():
        return None
    try:
        response = get_s3().get_object(
            Bucket=settings.S3_BUCKET,
            Key=f"articles/{article_id}/content.json",
        )
        return json.loads(response["Body"].read())
    except ClientError as e:
        if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
            return None
        raise


def load_article_document(article_id: str) -> bytes | None:
    if not _s3_configured():
        return None
    s3 = get_s3()
    try:
        response = s3.get_object(
            Bucket=settings.S3_BUCKET,
            Key=f"articles/{article_id}/document.bin",
        )
        return response["Body"].read()
    except ClientError as e:
        if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
            return None
        raise
