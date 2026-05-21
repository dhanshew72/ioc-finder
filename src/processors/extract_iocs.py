import anthropic
import base64

from models.extraction_result import ExtractionResult
from models.indicator_of_compromise import IndicatorOfCompromise
from utils.markdown import strip_markdown_fences

import json

MODEL_NAME = "claude-sonnet-4-6"
MAX_TOKENS = 16384
EXTRACTION_PROMPT = """
You are a cybersecurity threat intelligence analyst. You will be given a threat intelligence report in PDF format.
Your job is to extract all indicators of compromise (IOCs) and relevant threat context from the document.

Extract the following fields for every domain found:
- indicator: the cleaned, unfanged domain or ip (e.g. evil[.]com → evil.com, 127.0.0[.]1 → 127.0.0.1)
- ioc_type: one of [domain, subdomain, url]
- threat_actor: the APT group, threat actor, or campaign name associated with it (null if unknown)
- malware_family: the malware or tool associated with this domain (null if unknown)
- usage: one of [c2, phishing, malware_distribution, exfiltration, unknown]
- confidence: one of [high, medium, low] based on how explicitly the report associates this domain with malicious activity
- context: a single sentence from or summarizing the report that explains why this domain is flagged
- source_section: the section or page of the report where this was found (null if unclear)

Rules:
- Return ONLY valid JSON, no prose, no markdown, no backticks
- If a domain appears multiple times, include it only once, using the highest confidence occurrence
- Normalize defanged domains (hxxp, [.], etc.) to their real form
- Do not include legitimate vendor or research domains cited as references
- Do not hallucinate or infer domains not explicitly mentioned in the document
- Return empty list for "iocs" if none can be found or document doesn't

Return your response in this exact structure:
{
  "report_title": "string",
  "report_date": "string or null",
  "threat_actors": ["string"],
  "iocs": [
    {
      "domain": "string",
      "ioc_type": "string",
      "threat_actor": "string or null",
      "malware_family": "string or null",
      "usage": "string",
      "confidence": "string",
      "context": "string",
      "source_section": "string or null"
    }
  ],
  "total_domains_found": number
}"""


class ExtractIOCs(object):

    def __init__(self, pdf_bytes):
        self.client = anthropic.Anthropic()
        self.pdf_data = self._convert_pdf(pdf_bytes)

    def extract_iocs(self):
        raw_json = ""
        answer_stream = self.client.messages.stream(
            model=MODEL_NAME,
            max_tokens=MAX_TOKENS,
            messages=self._build_messages(),
        )
        with answer_stream as stream:
            for text in stream.text_stream:
                raw_json += text
        stripped_json = strip_markdown_fences(raw_json)
        json_data = json.loads(stripped_json)
        return self._parse(json_data)

    def _convert_pdf(self, pdf_bytes):
        return base64.standard_b64encode(pdf_bytes).decode()

    def _build_messages(self):
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": self.pdf_data,
                        },
                    },
                    {"type": "text", "text": EXTRACTION_PROMPT},
                ],
            }
        ]
        return messages

    def _parse(self, data: dict) -> ExtractionResult:
        ioc_data = data.get("iocs", [])
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
            for ioc in ioc_data
        ]
        return ExtractionResult(
            report_title=data["report_title"],
            report_date=data.get("report_date"),
            threat_actors=data.get("threat_actors", []),
            iocs=iocs,
            total_domains_found=data["total_domains_found"],
        )
