from fastapi import APIRouter
import boto3
from pydantic_models.auth_models import SignupRequest
from secret_keys import SecretKeys

secret_keys = SecretKeys()
cl_id = secret_keys.COGNITO_CLIENT_ID
cl_secret = secret_keys.COGNITO_CLIENT_SECRET

router = APIRouter()
cognito_client = boto3.client('cognito-idp', region_name=secret_keys.REGION_NAME)



@router.post("/signup")
def signup_user(req: SignupRequest):
    try:
        res = cognito_client.sign_up(
            ClientId=cl_id,
            Username=req.email,
            Password=req.password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': req.email
                },
                {
                    'Name': 'name',
                    'Value': req.name
                }
            ]
        )
        return {
            "message": "User signed up successfully",
            "user_sub": res['UserSub'],
            "code_delivery_details": res['CodeDeliveryDetails']
        }
    except(Exception) as e:
        return {
            "message": "User signup failed",
            "error": str(e)
        }
    # return {"message": "User signed up"}

