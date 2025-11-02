# Testing Guidance

## Tests for the API

### Single Turn Text-Only Converssation

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "prompt=What is the meaning of life?" \
  -F "personality=Rick" \
  -F "user_id=test_user" \
  -F "session_id=test_session_1"
```

### Testing a Multi-Turn Conversation

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "prompt=My name is Dazbo." \
  -F "personality=Rick" \
  -F "user_id=test_user" \
  -F "session_id=test_session_1"

curl -X POST "http://localhost:8000/chat" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "prompt=What is my name?" \
  -F "personality=Rick" \
  -F "user_id=test_user" \
  -F "session_id=test_session_1"
```
