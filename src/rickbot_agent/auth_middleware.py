from starlette.types import ASGIApp, Receive, Scope, Send, Message
from starlette.requests import Request
from starlette.responses import JSONResponse

from rickbot_agent.auth import verify_credentials
from rickbot_utils.config import logger


class AuthMiddleware:
    """
    Passive authentication middleware using ASGI interface.
    Sets 'user' in scope if token is valid.
    """
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                user = verify_credentials(token)
                if user:
                    scope["user"] = user
            except Exception as e:
                logger.error(f"AuthMiddleware: Token verification failed: {e}")
        
        await self.app(scope, receive, send)