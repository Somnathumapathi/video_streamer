from fastapi import APIRouter
import boto3
from pydantic_models.auth_models import SignupRequest
from secret_keys import SecretKeys
from helpers import auth_helper
from db.pgsdb import get_db
from sqlalchemy.orm import Session

secret_keys = SecretKeys()
cl_id = secret_keys.COGNITO_CLIENT_ID
cl_secret = secret_keys.COGNITO_CLIENT_SECRET

router = APIRouter()
cognito_client = boto3.client('cognito-idp', region_name=secret_keys.REGION_NAME)



@router.post("/signup")
def signup_user(req: SignupRequest, db: Session = Depends(get_db)):
    try:
        secret_hash = auth_helper.get_secret_hash(
            cl_id,
            cl_secret,
            req.email
        )
        cog_res = cognito_client.sign_up(
            ClientId=cl_id,
            Username=req.email,
            Password=req.password,
            SecretHash=secret_hash,
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
        if not cog_res["UserSub"]:
            return {
                "message": "User signup failed",
                "error": "Cognito Error"
            }
        user = User(
            name=req.name,
            email=req.email,
            cognito_sub=cog_res["UserSub"]
        )
        return {
            "message": "User signed up successfully, Verify your email",
            "response": res
        }
    except(Exception) as e:
        return {
            "message": "User signup failed",
            "error": str(e)
        }
    # return {"message": "User signed up"}

