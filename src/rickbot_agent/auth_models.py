from pydantic import BaseModel, EmailStr, Field


class AuthUser(BaseModel):
    """
    Represents an authenticated user in the system.
    This model is used to pass user information from the auth layer to the application.
    """

    id: str = Field(..., description="Subject ID from the provider")
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., description="User full name")
    provider: str = Field(..., description="Identity provider (google, github, mock)")


class PersonaAccessDeniedException(Exception):
    """Exception raised when a user does not have access to a persona."""

    def __init__(self, personality: str, required_role: str):
        self.personality = personality
        self.required_role = required_role
        self.detail = f"Upgrade Required: Access to the '{personality}' persona is restricted to {required_role.capitalize()}s."
        super().__init__(self.detail)
