import os

import requests
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from rickbot_agent.auth_models import AuthUser
from rickbot_utils.config import logger

security = HTTPBearer()


def verify_credentials(token: str) -> AuthUser | None:
    """
    Verifies the authentication token and returns an AuthUser object or None if invalid.
    """
    if not token or token == "undefined":
        return None

    user = None

    # 1. Check for Mock Token (Development Only)
    if token.startswith("mock:"):
        allow_mock = os.getenv("BACKEND_ALLOW_MOCK_AUTH")
        if allow_mock != "true":
            logger.warning(f"Mock auth failed. ALLOW_MOCK={allow_mock}")
            return None

        try:
            # Format: mock:id:email:name
            parts = token.split(":")
            if len(parts) < 4:
                logger.warning(f"Mock token malformed: {token}")
                return None

            user = AuthUser(id=parts[1], email=parts[2], name=parts[3], provider="mock")
        except Exception as e:
            logger.error(f"Mock auth exception: {e}")
            return None

    # 2. Try Google ID Token Verification
    if not user:
        try:
            google_client_id = os.getenv("GOOGLE_CLIENT_ID")
            if google_client_id:
                idinfo = id_token.verify_oauth2_token(
                    token, google_requests.Request(), google_client_id, clock_skew_in_seconds=10
                )
                user = AuthUser(
                    id=idinfo["sub"], email=idinfo["email"], name=idinfo.get("name", idinfo["email"]), provider="google"
                )
        except ValueError:
            pass
        except Exception as e:
            logger.error(f"Error verifying Google token: {e}")

    # 3. Try GitHub Access Token Verification
    if not user:
        try:
            github_response = requests.get("https://api.github.com/user", headers={"Authorization": f"token {token}"}, timeout=5)
            if github_response.status_code == 200:
                user_data = github_response.json()
                email = user_data.get("email")
                if not email:
                    emails_resp = requests.get(
                        "https://api.github.com/user/emails", headers={"Authorization": f"token {token}"}, timeout=5
                    )
                    if emails_resp.status_code == 200:
                        emails = emails_resp.json()
                        primary_email = next((e["email"] for e in emails if e["primary"]), emails[0]["email"] if emails else None)
                        email = primary_email

                user = AuthUser(
                    id=str(user_data["id"]),
                    email=email or f"{user_data['login']}@github.com",
                    name=user_data.get("name") or user_data["login"],
                    provider="github",
                )
        except Exception as e:
            logger.error(f"Error verifying GitHub token: {e}")

    return user


async def verify_token(request: Request, creds: HTTPAuthorizationCredentials = Depends(security)) -> AuthUser:
    """
    Dependency that enforces authentication.
    """
    # Check request.scope set by AuthMiddleware (ASGI style)
    user = request.scope.get("user")
    if user:
        return user

    raise HTTPException(status_code=401, detail="Invalid authentication credentials")