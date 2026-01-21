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
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.bucket_name = settings.S3_BUCKET_NAME
        self.prefix = settings.S3_KEY_PREFIX.rstrip("/") if settings.S3_KEY_PREFIX else ""


    def save(self, key: str, data: bytes, content_type: str = "") -> None:
        """Save file to S3"""
        try:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=key, Body=data, ContentType=content_type)
            logger.info("File saved to S3", bucket=self.bucket_name, key=key, size=len(data))
        except ClientError as e:
            logger.error("Failed to save to S3", bucket=self.bucket_name, key=key, error=str(e))
            raise

    def load(self, key: str) -> bytes:
        """Load file from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            data = response["Body"].read()
            logger.info("File loaded from S3", bucket=self.bucket_name, key=key, size=len(data))
            return data
        except ClientError as e:
            logger.error("Failed to load from S3", bucket=self.bucket_name, key=key, error=str(e))
            raise

    def delete(self, key: str) -> bool:
        """Delete file from S3"""
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

    def exists(self, key: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate presigned URL for downloading file"""
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in
            )
            logger.info("Generated presigned URL", bucket=self.bucket_name, key=key)
            return url
        except ClientError as e:
            logger.error("Failed to generate presigned URL", bucket=self.bucket_name, key=key, error=str(e))
            raise
