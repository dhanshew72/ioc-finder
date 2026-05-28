from extraction.utils.url import hash_url, read_url
from extraction.processors.extract_iocs import ExtractIOCs
from extraction.storage.s3 import S3Client
import dataclasses
import datetime
import json

BUCKET = "ioc-finder-data"


def _build_key(url: str, username: str) -> str:
    url_hash = hash_url(url)
    return f"processed/{username}/{url_hash}.json"


def main(event: dict, context=None) -> None:
    url = event["url"]
    username = event["username"]
    s3_client = S3Client(BUCKET)
    s3_path = _build_key(url, username)
    has_been_processed = s3_client.list_objects(prefix=s3_path)
    if has_been_processed:
        print(f"Already processed, skipping: {s3_path}")
        return

    pdf_bytes = read_url(url)
    result = ExtractIOCs(pdf_bytes, url).extract_iocs()
    json_data = dataclasses.asdict(result)
    output_bytes = json.dumps(json_data).encode("utf-8")
    s3_client.put_object(s3_path, output_bytes)
