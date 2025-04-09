from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
import boto3
from pydantic_models.auth_models import SignupRequest, LoginRequest, ConfirmationRequest
from secret_keys import SecretKeys
from helpers import auth_helper
from db.pgsdb import get_db
from sqlalchemy.orm import Session
from db.models.user import User
from db.middleware.auth_middleware import get_user

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
            raise HTTPException(
                status_code=400,
                detail="Cognito User signup failed"
            )
        user = User(
            name=req.name,
            email=req.email,
            cognito_sub=cog_res["UserSub"]
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "message": "User signed up successfully, Verify your email",
            "response": user
        }
    except(Exception) as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/login")
def login_user(req: LoginRequest, res: Response):
    try:
        secret_hash = auth_helper.get_secret_hash(
            cl_id,
            cl_secret,
            req.email
        )
        cog_res = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            ClientId=cl_id,
            # SecretHash=secret_hash,
            AuthParameters={
                'USERNAME': req.email,
                'PASSWORD': req.password,
                'SECRET_HASH': secret_hash
            }
        )
        auth_res = cog_res["AuthenticationResult"]
        if not auth_res:
            raise HTTPException(
                status_code=400,
                detail="Cognito User login failed"
            )
        res.set_cookie(
            key="access_token",
            value=auth_res["AccessToken"],
            httponly=True,
            secure=True,
            max_age=3600,
        )
        res.set_cookie(
            key="refresh_token",
            value=auth_res["RefreshToken"],
            httponly=True,
            secure=True,
            max_age=3600 * 24 * 30,
        )
        

        return {
            "message": "User logged in successfully",
            
        }
    except(Exception) as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.post("/confirm_user")
def confirm_user(req: ConfirmationRequest, db: Session = Depends(get_db)):
    try:
        secret_hash = auth_helper.get_secret_hash(
            cl_id,
            cl_secret,
            req.email
        )
        cog_res = cognito_client.confirm_sign_up(
            ClientId=cl_id,
            SecretHash=secret_hash,
            Username=req.email,
            ConfirmationCode=req.confirmation_code,
           
        )      
        

        return {
         "message": "User confirmation successful"
        }
    
    except(Exception) as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.post("/refresh_token")
def refresh_token(
    refresh_token: str = Cookie(None),
    user_cognito_sub: str = Cookie(None),
    res: Response = None,
):
    try:
        if not refresh_token or not user_cognito_sub:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated"
            )
        secret_hash = auth_helper.get_secret_hash(
            cl_id,
            cl_secret,
            user_cognito_sub
        )
        cog_res = cognito_client.initiate_auth(
            AuthFlow='REFRESH_TOKEN_AUTH',
            ClientId=cl_id,
            AuthParameters={
                'REFRESH_TOKEN': refresh_token,
                'SECRET_HASH': secret_hash
            }
        )
        auth_res = cog_res["AuthenticationResult"]
        if not auth_res:
            raise HTTPException(
                status_code=400,
                detail="Cognito User login failed"
            )
        res.set_cookie(
            key="access_token",
            value=auth_res["AccessToken"],
            httponly=True,
            secure=True,
            max_age=3600,
        )
        

        return {
            "message": "Access token refreshed successfully",
            
        }
    except(Exception) as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.get("/user")
def protected_route(user=Depends(get_user)):
    return {"message": "You are authenticated!", "user": user}
