from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize the Limiter
# We use get_remote_address as a default fallback, but we will likely override this
# with a custom key function in the main app or via dependency injection to handle
# authenticated users correctly.
limiter = Limiter(key_func=get_remote_address)
