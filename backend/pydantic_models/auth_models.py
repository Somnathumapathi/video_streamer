from pydantic import BaseModel

class SignupRequest(BaseModel):
    name: str    
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ConfirmationRequest(BaseModel):
    email: str
    confirmation_code: str