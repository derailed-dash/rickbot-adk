from starlette.types import ASGIApp, Receive, Scope, Send, Message
from starlette.requests import Request
from starlette.responses import JSONResponse

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
            except Exception as e:
                logger.error(f"AuthMiddleware: Token verification failed: {e}")
        
        await self.app(scope, receive, send)


class PersonaAccessMiddleware:
    """
    Middleware to enforce Role-Based Access Control (RBAC) for personas.
    Buffers the request body to peek at 'personality' and then replays it.
    """
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] not in ["/chat", "/chat_stream"]:
            await self.app(scope, receive, send)
            return

        # 1. Buffer all body messages
        body_messages = []
        more_body = True
        try:
            while more_body:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                body_messages.append(message)
                more_body = message.get("more_body", False)
        except Exception as e:
            logger.error(f"PersonaAccessMiddleware: Failed to read body: {e}")
            await self.app(scope, receive, send)
            return

        # 2. Check access using a temporary receiver
        check_messages = list(body_messages)
        async def check_receive() -> Message:
            if check_messages:
                return check_messages.pop(0)
            return {"type": "http.disconnect"}

        request = Request(scope, receive=check_receive)
        try:
            form_data = await request.form()
            personality = form_data.get("personality", "Rick")
            
            required_role = get_required_role(personality)
            user_role = "standard"
            
            user = scope.get("user")
            if user:
                user_role = get_user_role(user.id)

            if required_role == "supporter" and user_role != "supporter":
                logger.info(f"PersonaAccessMiddleware: ACCESS DENIED for user {user.id if user else 'anonymous'} to {personality}")
                response = JSONResponse(
                    status_code=403,
                    content={
                        "error_code": "UPGRADE_REQUIRED",
                        "detail": f"Upgrade Required: Access to the '{personality}' persona is restricted to Supporters.",
                        "required_role": required_role,
                        "personality": personality,
                    },
                )
                await response(scope, receive, send)
                return
        except Exception as e:
            logger.error(f"PersonaAccessMiddleware: Error checking access: {e}")

        # 3. Replay the buffered body messages to the application
        async def replay_receive() -> Message:
            if body_messages:
                return body_messages.pop(0)
            return {"type": "http.disconnect"}

        await self.app(scope, replay_receive, send)
