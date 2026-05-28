from typing import Optional

class IndicatorOfCompromise:
    domain: str
    ioc_type: str
    threat_actor: Optional[str]
    malware_family: Optional[str]
    usage: str
    confidence: str
    context: str
    source_section: Optional[str]
