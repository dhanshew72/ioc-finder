import dataclasses
import json
from utils.url import hash_url, read_url
from processors.extract_iocs import ExtractIOCs
from storage.s3 import S3Client
from storage.resources import S3Bucket
from models.extraction_list import ExtractionListEntry



def _update_entry(s3_client: S3Client, url: str, url_hash: str, email: str, report_title: str):
    entry = ExtractionListEntry(url=url, report_title=report_title, name=url_hash).as_dict()
    entries = s3_client.get_json_object(email)
    entries.append(entry)
    s3_path = f"processed/{email}/list.json"
    s3_client.put_object(s3_path, entries)

def main(event: dict, context=None) -> dict:
    url = event["url"]
    email = event["email"]
    s3_client = S3Client(S3Bucket.IOC_DATA)
    url_hash = hash_url(url)
    s3_path = f"processed/{email}/{url_hash}.json"
    has_been_processed = s3_client.list_objects(prefix=s3_path)
    if has_been_processed:
        print(f"Already processed, skipping: {s3_path}")
        return {"error": "Already processed, skipping"}
    pdf_bytes = read_url(url)
    result = ExtractIOCs(pdf_bytes, url).extract_iocs()
    json_data = dataclasses.asdict(result)
    output_bytes = json.dumps(json_data).encode("utf-8")
    s3_client.put_object(s3_path, output_bytes)
    _update_entry(s3_client, url, url_hash, email, result.report_title)
    return json_data
