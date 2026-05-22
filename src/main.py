import dataclasses
import datetime
import json
from utils.url import hash_url
from processors.extract_iocs import ExtractIOCs
from storage.s3 import S3Client

BUCKET = "ioc-finder-data"


def _build_key(url: str) -> str:
    url_hash = hash_url(url)
    date = datetime.date.today().isoformat()
    return f"processed/{date}/{url_hash}.json"


def main(event: dict, context=None) -> None:
    url = event["url"]
    s3_client = S3Client(BUCKET)
    s3_path = _build_key(url)

    existing = s3_client.list_objects(prefix=s3_path)
    if existing:
        print(f"Already processed, skipping: {s3_path}")
        return

    result = ExtractIOCs(url).extract_iocs()
    json_data = dataclasses.asdict(result)
    output_bytes = json.dumps(json_data).encode("utf-8")
    s3_client.put_object(s3_path, output_bytes)


if __name__ == '__main__':
    event = {
        "url": "https://unit42.paloaltonetworks.com/domain-shadowing/?pdf=download&lg=en&_wpnonce=2c5aefd0ad"
    }
    main(event)
