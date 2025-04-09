from fastapi import Cookie, HTTPException
import boto3
from secret_keys import SecretKeys

cognito_client = boto3.client('cognito-idp', region_name=SecretKeys().REGION_NAME)

def _get_user_from_cognito(access_token: str):
    try:
        user_res = cognito_client.get_user(
            AccessToken=access_token
        )
        return {
            x["Name"]: x["Value"]
            for x in user_res.get("UserAttributes", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
def get_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    return _get_user_from_cognito(access_token)