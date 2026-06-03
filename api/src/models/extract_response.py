from typing import Optional
from pydantic import BaseModel


class ExtractResponse(BaseModel):
    report_title: str
    report_date: Optional[str]
    threat_actors: list[str]
    iocs: list
    total_domains_found: int
    source_url: str
