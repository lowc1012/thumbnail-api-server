import boto3
from botocore.exceptions import ClientError
from app.internal.log.logger import get_logger
from app.internal.configuration.settings import Settings

logger = get_logger()


class StorageService:
    def __init__(self, settings: Settings):
        """Initialize storage service"""
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            region_name=settings.S3_REGION,
            aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
            aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
        )
        self.endpoint_url = getattr(settings, "S3_ENDPOINT_URL")
        self.bucket_name = getattr(settings, "S3_BUCKET_NAME")
        self.prefix = getattr(settings, "S3_KEY_PREFIX", "").rstrip("/")

    def _get_key(self, file_path: str) -> str:
        """Get full S3 key with prefix"""
        if self.prefix:
            return f"{self.prefix}/{file_path}"
        return file_path

    def save(self, file_path: str, data: bytes, content_type: str = "") -> str:
        """Save file to S3"""
        key = self._get_key(file_path)
        self.s3_client.put_object(Bucket=self.bucket_name, Key=key, Body=data, ContentType=content_type)
        logger.info(
            "File saved to S3", bucket=self.bucket_name, key=key, size=len(data)
        )
        return key

    def load(self, file_path: str) -> bytes:
        """Load file from S3"""
        key = self._get_key(file_path)

        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)

        data = response["Body"].read()
        logger.info(
            "File loaded from S3", bucket=self.bucket_name, key=key, size=len(data)
        )
        return data

    def delete(self, file_path: str) -> bool:
        """Delete file from S3"""
        key = self._get_key(file_path)

        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info("File deleted from S3", bucket=self.bucket_name, key=key)
            return True
        except ClientError as e:
            logger.error(
                "Failed to delete from S3",
                bucket=self.bucket_name,
                key=key,
                error=str(e),
            )
            return False

    def exists(self, file_path: str) -> bool:
        """Check if file exists in S3"""
        key = self._get_key(file_path)

        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False
