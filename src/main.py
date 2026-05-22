from processors.extract_iocs import ExtractIOCs

def main(event: dict, context = None) -> None:
    url = event["url"]
    result = ExtractIOCs(url).extract_iocs()
    print(result)


if __name__ == '__main__':
    event = {
        "url": "https://unit42.paloaltonetworks.com/domain-shadowing/?pdf=download&lg=en&_wpnonce=2c5aefd0ad"
    }
    main(event)
