from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request
from starlette.responses import JSONResponse
import json

from rickbot_agent.auth import verify_credentials
from rickbot_agent.auth_models import PersonaAccessDeniedException
from rickbot_agent.services import get_required_role, get_user_role
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
            except Exception:
                pass
        
        await self.app(scope, receive, send)


class PersonaAccessMiddleware:
    """
    Middleware to enforce Role-Based Access Control (RBAC) for personas.
    Uses a custom receive to allow multiple reads of the body.
    """
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] not in ["/chat", "/chat_stream"]:
            await self.app(scope, receive, send)
            return

        # 1. Capture the body so we can read it and still pass it along
        body = b""
        more_body = True
        while more_body:
            message = await receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        # 2. Extract personality from body
        # Since it's multipart/form-data or urlencoded, we can use Request.form()
        # but we need a custom receive that returns the body we just read.
        
        async def cached_receive() -> dict:
            return {"type": "http.request", "body": body, "more_body": False}

        request = Request(scope, receive=cached_receive)
        try:
            form_data = await request.form()
            personality = form_data.get("personality", "Rick")
            
            required_role = get_required_role(personality)
            user_role = "standard"
            user = scope.get("user")
            if user:
                user_role = get_user_role(user.id)

            if required_role == "supporter" and user_role != "supporter":
                from src.main import persona_access_denied_handler
                response = persona_access_denied_handler(request, PersonaAccessDeniedException(personality, required_role))
                await response(scope, receive, send)
                return
        except Exception as e:
            logger.error(f"Error in PersonaAccessMiddleware: {e}")

        # 3. Continue with cached receive
        await self.app(scope, cached_receive, send)