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

    def parse(self, data: dict) -> "ExtractionResult":
        iocs = [
            IndicatorOfCompromise(
                domain=ioc["domain"],
                ioc_type=ioc["ioc_type"],
                threat_actor=ioc.get("threat_actor"),
                malware_family=ioc.get("malware_family"),
                usage=ioc["usage"],
                confidence=ioc["confidence"],
                context=ioc["context"],
                source_section=ioc.get("source_section"),
            )
            for ioc in data.get("iocs", [])
        ]
        return ExtractionResult(
            report_title=data["report_title"],
            report_date=data.get("report_date"),
            threat_actors=data.get("threat_actors", []),
            iocs=iocs,
            total_domains_found=data["total_domains_found"],
        )
