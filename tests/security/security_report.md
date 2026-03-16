# Security Findings

## 1. Input Validation

Some API endpoints accept raw input without strict validation.

Example:
POST /api/tasks

Potential risk:
Injection attacks if input is not sanitized.

Recommendation:
Validate and sanitize all user inputs.

---

## 2. Error Information Exposure

Some API errors expose internal stack traces.

Example response:

{
  "error": "database connection failed"
}

Risk:
Attackers can gather internal system information.

Recommendation:
Return generic error messages.

---

## 3. CORS Configuration

CORS appears to allow all origins.

Risk:
External domains may interact with the API.

Recommendation:
Restrict allowed origins.

---

## 4. Missing Rate Limiting

No rate limiting detected on API endpoints.

Risk:
Possible brute-force or denial-of-service attacks.

Recommendation:
Implement rate limiting using middleware.