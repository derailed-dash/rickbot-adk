import os
import requests
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rickbot_agent.auth_models import AuthUser
from rickbot_utils.config import logger

security = HTTPBearer()

async def verify_token(creds: HTTPAuthorizationCredentials = Depends(security)) -> AuthUser:
    """
    Verifies the authentication token and returns an AuthUser object.
    Supports:
    - Mock tokens (format: \"mock:id:email:name\") - Development only
    - Google ID Tokens
    - GitHub Access Tokens
    """
    token = creds.credentials
    if not token:
         raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    # 1. Check for Mock Token (Development Only)
    if token.startswith("mock:"):
        # In a real app, you'd check an environment variable to ensure this is only enabled in dev
        allow_mock = os.getenv("NEXT_PUBLIC_ALLOW_MOCK_AUTH")
        
        if allow_mock != "true":
             logger.warning(f"Mock auth failed. ALLOW_MOCK={allow_mock}")
             raise HTTPException(status_code=401, detail="Mock authentication is disabled")
             
        try:
            # Format: mock:id:email:name
            parts = token.split(":")
            if len(parts) < 4:
                 logger.warning(f"Mock token malformed: {token}")
                 raise HTTPException(status_code=401, detail="Malformed mock token")
            
            return AuthUser(
                id=parts[1],
                email=parts[2],
                name=parts[3],
                provider="mock"
            )
        except Exception as e:
             logger.error(f"Mock auth exception: {e}")
             raise HTTPException(status_code=401, detail="Invalid mock token")

    # 2. Try Google ID Token Verification
    try:
        # We need the client ID to verify the token
        google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        if google_client_id:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), google_client_id)
            
            return AuthUser(
                id=idinfo['sub'],
                email=idinfo['email'],
                name=idinfo.get('name', idinfo['email']),
                provider="google"
            )
    except ValueError:
        # Not a valid Google token or verification failed, continue to next provider
        pass
    except Exception as e:
        logger.error(f"Error verifying Google token: {e}")

    # 3. Try GitHub Access Token Verification
    try:
        # GitHub tokens are opaque, we must call their API
        github_response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {token}"},
            timeout=5
        )
        if github_response.status_code == 200:
            user_data = github_response.json()
            # GitHub email might be private, so we might need another call if email is null
            email = user_data.get("email")
            if not email:
                 # Try to get emails
                 emails_resp = requests.get(
                     "https://api.github.com/user/emails",
                     headers={"Authorization": f"token {token}"},
                     timeout=5
                 )
                 if emails_resp.status_code == 200:
                     emails = emails_resp.json()
                     # Find primary or first
                     primary_email = next((e['email'] for e in emails if e['primary']), emails[0]['email'] if emails else None)
                     email = primary_email

            return AuthUser(
                id=str(user_data['id']),
                email=email or f"{user_data['login']}@github.com",
                name=user_data.get('name') or user_data['login'],
                provider="github"
            )
    except Exception as e:
        logger.error(f"Error verifying GitHub token: {e}")
    
    # Default reject
    raise HTTPException(status_code=401, detail="Invalid authentication credentials")
