from models.indicator_of_compromise import IndicatorOfCompromise
from models.extraction_result import ExtractionResult
from processors.extract_iocs import ExtractIOCs
from utils.markdown import strip_markdown_fences
import json
import os
import sys
from pathlib import Path

def parse_result(data: dict) -> ExtractionResult:
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


def write_json(path: str, result: ExtractionResult) -> None:
    data = {
        "report_title": result.report_title,
        "report_date": result.report_date,
        "threat_actors": result.threat_actors,
        "iocs": [
            {
                "domain": ioc.domain,
                "ioc_type": ioc.ioc_type,
                "threat_actor": ioc.threat_actor,
                "malware_family": ioc.malware_family,
                "usage": ioc.usage,
                "confidence": ioc.confidence,
                "context": ioc.context,
                "source_section": ioc.source_section,
            }
            for ioc in result.iocs
        ],
        "total_domains_found": result.total_domains_found,
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path/to/report.pdf>", file=sys.stderr)
        sys.exit(1)

    pdf_path = sys.argv[1]

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY environment variable is not set", file=sys.stderr)
        sys.exit(1)

    raw_json = ExtractIOCs(pdf_bytes).extract_iocs()
    if not raw_json:
        print("no text content in response", file=sys.stderr)
        sys.exit(1)

    raw_json = strip_markdown_fences(raw_json)

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        print(f"Raw response:\n{raw_json}", file=sys.stderr)
        print(f"failed to parse JSON response: {e}", file=sys.stderr)
        sys.exit(1)

    result = parse_result(data)

    stem = Path(pdf_path).stem

    json_path = f"{stem}_iocs.json"
    write_json(json_path, result)
    print(f"JSON written to {json_path}", file=sys.stderr)
    print(f"Report: {result.report_title}")
    if result.report_date:
        print(f"Date:   {result.report_date}")
    if result.threat_actors:
        print(f"Actors: {', '.join(result.threat_actors)}")
    print(f"IOCs:   {result.total_domains_found} domains extracted")


if __name__ == "__main__":
    main()
