import boto3

def get_secret(secret_name: str):
    client = boto3.client("secretsmanager")
    secret = client.get_secret_value(
        SecretId=secret_name
    )
    return secret["SecretString"]
