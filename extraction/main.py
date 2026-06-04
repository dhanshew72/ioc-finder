from processors.export_iocs import ExportIOCs
from utils.url import hash_url, read_url
from processors.extract_iocs import ExtractIOCs
from storage.s3 import S3Client
from storage.resources import S3Bucket

def _has_been_processed(url_hash: str, prefix: str):
    s3_client = S3Client(S3Bucket.IOC_DATA)
    return s3_client.list_objects(prefix=f"{prefix}/{url_hash}.json")


def main(event: dict, context=None) -> dict:
    url = event["url"]
    email = event["email"]
    prefix = f"processed/{email}"
    url_hash = hash_url(url)
    if _has_been_processed(url_hash, prefix):
        return {"error": f"Already processed url: {url} with email: {email}, skipping"}
    pdf_bytes = read_url(url)
    result = ExtractIOCs(pdf_bytes, url).extract_iocs()
    export_iocs = ExportIOCs(result, prefix, url_hash, email)
    export_iocs.export()
    return export_iocs.json_data
