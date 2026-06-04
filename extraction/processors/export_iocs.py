import dataclasses
from models.extraction_result import ExtractionResult
from models.extraction_list import ExtractionListEntry
from storage.s3 import S3Client
from storage.resources import S3Bucket
import json

class ExportIOCs:

    def __init__(self, result: ExtractionResult, prefix: str, url_hash: str, email: str):
        self.result = result
        self.url_hash = url_hash
        self.prefix = prefix
        self.email = email
        self.client = S3Client(S3Bucket.IOC_DATA)
        self.json_data = dataclasses.asdict(self.result)

    def export(self):
        output_bytes = json.dumps(self.json_data).encode("utf-8")
        self.client.put_object(f"{self.prefix}/{self.url_hash}.json", output_bytes)
        self._update_entry()

    def _update_entry(self):
        entry = ExtractionListEntry(
            url=self.result.source_url,
            report_title=self.result.report_title,
            name=self.url_hash
        )
        try:
            entries = self.client.get_json_object(self.email)
        except:
            entries = []
        entries.append(dataclasses.asdict(entry))
        s3_path = f"processed/{self.email}/list.json"
        self.client.put_object(s3_path, json.dumps(entries).encode("utf-8"))
