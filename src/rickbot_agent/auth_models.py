from pydantic import BaseModel, Field, EmailStr

class AuthUser(BaseModel):
    """
    Represents an authenticated user in the system.
    This model is used to pass user information from the auth layer to the application.
    """
    id: str = Field(..., description="Subject ID from the provider")
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., description="User full name")
    provider: str = Field(..., description="Identity provider (google, github, mock)")
