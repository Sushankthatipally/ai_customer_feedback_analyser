"""
AWS S3 Service for File Storage
Handles file uploads, downloads, and management in AWS S3
"""
import os
import logging
from typing import Optional, BinaryIO, Dict, Any
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import aioboto3
from io import BytesIO

logger = logging.getLogger(__name__)


class S3Service:
    """Service for managing files in AWS S3"""
    
    def __init__(self):
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.s3_bucket = os.getenv("AWS_S3_BUCKET")
        
        if not all([self.aws_access_key, self.aws_secret_key, self.s3_bucket]):
            logger.warning("AWS credentials not configured. S3 storage will not be available.")
            self.enabled = False
            return
        
        self.enabled = True
        
        # Configure boto3 client
        self.config = Config(
            region_name=self.aws_region,
            signature_version='s3v4',
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            }
        )
        
        # Synchronous client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            config=self.config
        )
        
        # Async session for aioboto3
        self.session = aioboto3.Session(
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )
    
    def _ensure_enabled(self):
        """Ensure S3 service is enabled"""
        if not self.enabled:
            raise ValueError("S3 service is not enabled. Check AWS credentials.")
    
    def _generate_key(self, tenant_id: int, filename: str, prefix: str = "uploads") -> str:
        """
        Generate S3 object key with tenant isolation
        
        Args:
            tenant_id: Tenant ID for isolation
            filename: Original filename
            prefix: Folder prefix (uploads, exports, reports, etc.)
            
        Returns:
            S3 object key
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = filename.replace(" ", "_")
        return f"{prefix}/tenant_{tenant_id}/{timestamp}_{safe_filename}"
    
    async def upload_file_async(
        self,
        file_obj: BinaryIO,
        filename: str,
        tenant_id: int,
        prefix: str = "uploads",
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to S3 asynchronously
        
        Args:
            file_obj: File object or bytes
            filename: Original filename
            tenant_id: Tenant ID
            prefix: S3 folder prefix
            content_type: MIME type
            metadata: Additional metadata
            
        Returns:
            Dict with S3 key, bucket, and URL
        """
        self._ensure_enabled()
        
        s3_key = self._generate_key(tenant_id, filename, prefix)
        
        # Prepare extra args
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        if metadata:
            extra_args['Metadata'] = metadata
        
        try:
            async with self.session.client('s3', config=self.config) as s3:
                await s3.upload_fileobj(
                    file_obj,
                    self.s3_bucket,
                    s3_key,
                    ExtraArgs=extra_args
                )
            
            logger.info(f"File uploaded to S3: {s3_key}")
            
            return {
                "bucket": self.s3_bucket,
                "key": s3_key,
                "url": f"https://{self.s3_bucket}.s3.{self.aws_region}.amazonaws.com/{s3_key}",
                "filename": filename,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise
    
    def upload_file(
        self,
        file_path: str,
        tenant_id: int,
        prefix: str = "uploads",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to S3 synchronously
        
        Args:
            file_path: Path to local file
            tenant_id: Tenant ID
            prefix: S3 folder prefix
            metadata: Additional metadata
            
        Returns:
            Dict with S3 key, bucket, and URL
        """
        self._ensure_enabled()
        
        filename = os.path.basename(file_path)
        s3_key = self._generate_key(tenant_id, filename, prefix)
        
        extra_args = {}
        if metadata:
            extra_args['Metadata'] = metadata
        
        try:
            self.s3_client.upload_file(
                file_path,
                self.s3_bucket,
                s3_key,
                ExtraArgs=extra_args
            )
            
            logger.info(f"File uploaded to S3: {s3_key}")
            
            return {
                "bucket": self.s3_bucket,
                "key": s3_key,
                "url": f"https://{self.s3_bucket}.s3.{self.aws_region}.amazonaws.com/{s3_key}",
                "filename": filename,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise
    
    async def download_file_async(
        self,
        s3_key: str,
        local_path: Optional[str] = None
    ) -> bytes:
        """
        Download file from S3 asynchronously
        
        Args:
            s3_key: S3 object key
            local_path: Optional local file path to save
            
        Returns:
            File content as bytes
        """
        self._ensure_enabled()
        
        try:
            async with self.session.client('s3', config=self.config) as s3:
                response = await s3.get_object(Bucket=self.s3_bucket, Key=s3_key)
                content = await response['Body'].read()
                
                if local_path:
                    with open(local_path, 'wb') as f:
                        f.write(content)
                    logger.info(f"File downloaded from S3 to: {local_path}")
                
                return content
        
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            raise
    
    def download_file(
        self,
        s3_key: str,
        local_path: str
    ) -> None:
        """
        Download file from S3 synchronously
        
        Args:
            s3_key: S3 object key
            local_path: Local file path to save
        """
        self._ensure_enabled()
        
        try:
            self.s3_client.download_file(
                self.s3_bucket,
                s3_key,
                local_path
            )
            logger.info(f"File downloaded from S3 to: {local_path}")
        
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            raise
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if successful
        """
        self._ensure_enabled()
        
        try:
            self.s3_client.delete_object(
                Bucket=self.s3_bucket,
                Key=s3_key
            )
            logger.info(f"File deleted from S3: {s3_key}")
            return True
        
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {e}")
            raise
    
    def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
        operation: str = "get_object"
    ) -> str:
        """
        Generate presigned URL for temporary access
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration in seconds (default 1 hour)
            operation: S3 operation (get_object or put_object)
            
        Returns:
            Presigned URL
        """
        self._ensure_enabled()
        
        try:
            url = self.s3_client.generate_presigned_url(
                operation,
                Params={'Bucket': self.s3_bucket, 'Key': s3_key},
                ExpiresIn=expiration
            )
            logger.info(f"Generated presigned URL for: {s3_key}")
            return url
        
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    def list_files(
        self,
        tenant_id: int,
        prefix: str = "uploads",
        max_keys: int = 1000
    ) -> list:
        """
        List files for a specific tenant
        
        Args:
            tenant_id: Tenant ID
            prefix: Folder prefix
            max_keys: Maximum number of files to return
            
        Returns:
            List of file metadata
        """
        self._ensure_enabled()
        
        tenant_prefix = f"{prefix}/tenant_{tenant_id}/"
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=tenant_prefix,
                MaxKeys=max_keys
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj['ETag']
                })
            
            return files
        
        except ClientError as e:
            logger.error(f"Error listing files from S3: {e}")
            raise
    
    def get_file_metadata(self, s3_key: str) -> Dict[str, Any]:
        """
        Get metadata for a specific file
        
        Args:
            s3_key: S3 object key
            
        Returns:
            File metadata
        """
        self._ensure_enabled()
        
        try:
            response = self.s3_client.head_object(
                Bucket=self.s3_bucket,
                Key=s3_key
            )
            
            return {
                'key': s3_key,
                'size': response['ContentLength'],
                'content_type': response.get('ContentType'),
                'last_modified': response['LastModified'].isoformat(),
                'metadata': response.get('Metadata', {}),
                'etag': response['ETag']
            }
        
        except ClientError as e:
            logger.error(f"Error getting file metadata from S3: {e}")
            raise
    
    def copy_file(
        self,
        source_key: str,
        dest_key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Copy file within S3
        
        Args:
            source_key: Source S3 object key
            dest_key: Destination S3 object key
            metadata: Optional new metadata
            
        Returns:
            Copy result
        """
        self._ensure_enabled()
        
        try:
            copy_source = {'Bucket': self.s3_bucket, 'Key': source_key}
            
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
                extra_args['MetadataDirective'] = 'REPLACE'
            
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.s3_bucket,
                Key=dest_key,
                **extra_args
            )
            
            logger.info(f"File copied in S3: {source_key} -> {dest_key}")
            
            return {
                'source_key': source_key,
                'dest_key': dest_key,
                'bucket': self.s3_bucket
            }
        
        except ClientError as e:
            logger.error(f"Error copying file in S3: {e}")
            raise


# Singleton instance
s3_service = S3Service()
