from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from rickbot_agent.auth import verify_credentials
from rickbot_agent.auth_models import PersonaAccessDeniedException
from rickbot_agent.services import get_required_role, get_user_role


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
                # Swallow exceptions to allow non-authenticated requests to proceed.
                # Invalid tokens will result in request.state.user being None.
                pass
        response = await call_next(request)
        return response


class PersonaAccessMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce Role-Based Access Control (RBAC) for personas.
    It checks if the requesting user has the required role for the selected persona.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # We only care about /chat and /chat_stream endpoints
        if request.url.path in ["/chat", "/chat_stream"]:
            # 1. Get requested personality
            # Since these endpoints use Form data, we need to peek at the form
            personality = "Rick"  # Default
            try:
                form_data = await request.form()
                personality = form_data.get("personality", "Rick")
            except Exception:
                # If we can't read the form (e.g. not multipart), just proceed
                pass

            # 2. Get required role for persona
            required_role = get_required_role(personality)

            # 3. Get user role
            user_role = "standard"
            user = getattr(request.state, "user", None)
            if user:
                user_role = get_user_role(user.email)

            # 4. Check access
            # Simple hierarchy: supporter > standard
            if required_role == "supporter" and user_role != "supporter":
                # We raise the exception, which will be caught by the FastAPI exception handler
                # However, Starlette's BaseHTTPMiddleware has issues with exception handlers.
                # See: https://github.com/fastapi/fastapi/issues/4518
                # To be safe, we'll use the handler manually or return the response.
                # Actually, raising inside dispatch() of BaseHTTPMiddleware DOES NOT trigger app exception handlers.
                # So we must return the JSONResponse directly or use a different middleware style.

                # Manual invocation of the handler logic for consistency
                from src.main import persona_access_denied_handler
                return persona_access_denied_handler(request, PersonaAccessDeniedException(personality, required_role))

        return await call_next(request)
