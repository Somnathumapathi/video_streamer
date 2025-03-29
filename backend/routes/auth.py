from fastapi import APIRouter
import boto3

router = APIRouter()
cognito_client = boto3.client('cognito-idp', region_name='ap-south-1')

@router.post("/signup")
def signup_user():
    return {"message": "User signed up"}
