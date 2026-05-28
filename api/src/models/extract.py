from pydantic import BaseModel, HttpUrl
from typing import Optional
from models.indicator_of_compromise import IndicatorOfCompromise

class ExtractRequest(BaseModel):
    url: HttpUrl


class ExtractResponse(BaseModel):
    report_title: str
    report_date: Optional[str]
    threat_actors: list[str]
    iocs: list[IndicatorOfCompromise]
    total_domains_found: int
    source_url: str
