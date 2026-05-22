import datetime
import hashlib
import json

from processors.extract_iocs import ExtractIOCs
from storage.s3 import S3Client

BUCKET = "ioc-finder-data"


def _s3_key(url: str) -> str:
    url_hash = hashlib.sha256(url.encode()).hexdigest()
    date = datetime.date.today().isoformat()
    return f"processed/{date}/{url_hash}.json"


def main(event: dict, context=None) -> None:
    url = event["url"]
    s3 = S3Client(BUCKET)
    s3_path = _s3_key(url)

    existing = s3.list_objects(prefix=s3_path)
    if existing:
        print(f"Already processed, skipping: {s3_path}")
        return

    result = ExtractIOCs(url).extract_iocs()
    output_bytes = json.dumps(result).encode("utf-8")
    s3.put_object(s3_path, output_bytes)


if __name__ == '__main__':
    event = {
        "url": "https://unit42.paloaltonetworks.com/domain-shadowing/?pdf=download&lg=en&_wpnonce=2c5aefd0ad"
    }
    main(event)
