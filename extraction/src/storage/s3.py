import boto3


class S3Client:

    def __init__(self, bucket: str):
        self.bucket = bucket
        self._client = boto3.client("s3")

    def list_objects(self, prefix: str = "") -> list[str]:
        keys = []
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
        return keys

    def get_object(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    def put_object(self, key: str, body: bytes) -> None:
        self._client.put_object(Bucket=self.bucket, Key=key, Body=body)

    def delete_object(self, key: str) -> None:
        self._client.delete_object(Bucket=self.bucket, Key=key)
