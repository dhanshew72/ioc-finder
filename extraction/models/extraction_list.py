from dataclasses import dataclass, asdict


@dataclass
class ExtractionListEntry:
    url: str
    report_title: str
    name: str
