from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from rickbot_agent.auth import verify_credentials


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Passive authentication: Attempt to verify, but don't fail if we can't.
        # This allows endpoints that don't need auth to proceed,
        # and allows endpoints that DO need auth to check request.state.user later.
        # 1. Extract token from header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                # 2. Verify credentials
                user = verify_credentials(token)
                if user:
                    request.state.user = user
            except Exception:
                # Log? Maybe too verbose if bad tokens are common spam
                pass
        
        response = await call_next(request)
        return response
