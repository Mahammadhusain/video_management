from pydantic import BaseModel, EmailStr, Field,ConfigDict

# Schema for Video create 
class VideoCreate(BaseModel):
    name: str
    size: float

# Schema for Video response
class VideoResponse(BaseModel):
    id: int
    name: str
    size: float
    path: str
    is_blocked: int

    model_config = ConfigDict(from_attributes=True)

# Schema for Token data access
class TokenData(BaseModel):
    username: str | None = None

# Schema for creating a new user
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(...)
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)

# Schema for returning a token after successful authentication
class Token(BaseModel):
    username: str
    email: EmailStr
    access_token: str
    token_type: str

# Schema for user login
class UserLogin(BaseModel):
    username: str
    password: str