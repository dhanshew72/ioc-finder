from models.indicator_of_compromise import IndicatorOfCompromise
from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class ExtractionResult:
    report_title: str
    report_date: Optional[str]
    threat_actors: list[str]
    iocs: list[IndicatorOfCompromise]
    total_domains_found: int

    def write_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.__dict__, f, indent=4)