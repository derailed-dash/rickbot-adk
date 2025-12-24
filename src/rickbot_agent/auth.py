from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from src.rickbot_agent.auth_models import AuthUser

async def verify_token(creds: HTTPAuthorizationCredentials) -> AuthUser:
    """
    Verifies the authentication token and returns an AuthUser object.
    Currently supports:
    - Mock tokens (format: "mock:id:email:name")
    """
    token = creds.credentials
    if not token:
         raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    if token.startswith("mock:"):
        try:
            # Format: mock:id:email:name
            parts = token.split(":")
            # parts[0] is 'mock'
            if len(parts) < 4:
                 raise HTTPException(status_code=401, detail="Malformed mock token")
            
            user_id = parts[1]
            email = parts[2]
            name = parts[3]
            
            return AuthUser(
                id=user_id,
                email=email,
                name=name,
                provider="mock"
            )
        except Exception:
             raise HTTPException(status_code=401, detail="Invalid mock token")
    
    # Default reject for now until real auth is implemented
    raise HTTPException(status_code=401, detail="Invalid authentication credentials")
