from fastapi import APIRouter
from models.extract import ExtractRequest

router = APIRouter()

@router.post("/extract")
def extract_data(body: ExtractRequest):
    # TODO: implement extraction logic
    return {"url": str(body.url), "iocs": []}


@router.get("/extract")
def extract_list():
    return {}


@router.get("/extract/{id}")
def extract_id():
    return {}
