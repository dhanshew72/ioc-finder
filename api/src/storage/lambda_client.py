import boto3
import json
from storage.resources import LambdaFunction


class LambdaClient:

    def __init__(self, name: LambdaFunction):
        self.name = name
        self._client = boto3.client("lambda")

    def invoke_get_response(self, payload: dict) -> dict:
        response = self._client.invoke(
            FunctionName=self.name,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )
        return json.loads(response["Payload"].read())
