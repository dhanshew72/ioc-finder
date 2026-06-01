from fastapi import APIRouter, Request, HTTPException
from botocore.exceptions import ClientError
from models.extract import ExtractRequest, ExtractResponse
from storage.lambda_client import LambdaClient
from storage.s3_client import S3Client
from storage.resources import LambdaFunction, S3Bucket

router = APIRouter(prefix='/extract')


@router.post("/", response_model=ExtractResponse)
def extract_data(request: Request, body: ExtractRequest):
    email = request.state.user["email"]
    payload = {"email": email, "url": body.url}
    result = LambdaClient(LambdaFunction.IOC_EXTRACTION).invoke_get_response(payload)
    return ExtractResponse(**result)


@router.get("/")
def extract_list(request: Request):
    email = request.state.user["email"]
    s3_client = S3Client(S3Bucket.IOC_DATA)
    try:
        return s3_client.get_json_object(f"processed/{email}/list.json")
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return []
        raise


@router.get("/{id}", response_model=ExtractResponse)
def extract_id(extraction_id: str, request: Request):
    email = request.state.user["email"]
    s3 = S3Client(S3Bucket.IOC_DATA)
    try:
        data = s3.get_json_object(f"processed/{email}/{extraction_id}.json")
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            raise HTTPException(status_code=404, detail=f"Extraction {extraction_id} not found")
        raise
    return ExtractResponse(**data)
