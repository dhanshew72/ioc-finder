from enum import Enum


class S3Bucket(str, Enum):
    IOC_DATA = "ioc-finder-data"


class LambdaFunction(str, Enum):
    IOC_EXTRACTION = "ioc-extraction"
