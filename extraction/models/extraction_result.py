from models.indicator_of_compromise import IndicatorOfCompromise
from dataclasses import dataclass
from typing import Optional

@dataclass
class ExtractionResult:
    report_title: str
    report_date: Optional[str]
    threat_actors: list[str]
    iocs: list[IndicatorOfCompromise]
    total_domains_found: int
    source_url: str
