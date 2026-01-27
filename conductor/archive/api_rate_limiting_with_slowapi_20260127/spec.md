# Specification: API Rate Limiting with slowapi

## Overview
Implement API rate limiting to protect the Rickbot-ADK backend from abuse, ensure fair resource allocation (especially for LLM calls), and improve overall system stability. We will use the `slowapi` library, which is a FastAPI port of `limits`.

## Functional Requirements
- **Global Rate Limiting:** Apply a default safety-net rate limit to all API endpoints.
- **Endpoint-Specific Limits:** Apply stricter limits to resource-intensive endpoints, specifically LLM generation.
- **Identifier Strategy:** 
    - Authenticated users: Limit by User ID (extracted from JWT).
    - Unauthenticated requests: Limit by Client IP address.
- **Error Handling:** Return a standard `429 Too Many Requests` response when a limit is exceeded, including a `Retry-After` header if possible.

## Rate Limit Policies
| Scope | Limit | Identifier |
| :--- | :--- | :--- |
| Global (Default) | 60 requests per minute | User ID / IP |
| LLM Generation (`/chat`, etc.) | 5 requests per minute | User ID / IP |

## Non-Functional Requirements
- **Performance:** Rate limiting checks should add minimal latency to API requests.
- **Maintainability:** Use `slowapi` decorators for clear and concise configuration.
- **Observability:** Log rate limit hits (exceeding the limit) for monitoring.

## Acceptance Criteria
- [ ] Global rate limit of 60/minute is enforced across all endpoints.
- [ ] LLM generation endpoints are restricted to 5/minute per user/IP.
- [ ] Exceeding a limit returns a `429` status code.
- [ ] Authenticated users are tracked by their unique ID.
- [ ] Unauthenticated users are tracked by IP.
- [ ] Unit tests verify rate limiting logic and identifier extraction.

## Documentation Updates
- Update `README.md` to mention rate limiting features.
- Update `docs/design.md` to document the rate limiting architecture and policies.

## Out of Scope
- Distributed rate limiting using Redis (will use in-memory storage for now).
- Complex tiered pricing/limit models.
- IP Whitelisting/Blacklisting management UI.
