## 1. Request a User Account via Swagger API

The VariantValidator API provides a Swagger interface to submit account requests interactively or via JSON requests.

1. Navigate to [https://www183.lamp.le.ac.uk/](https://www183.lamp.le.ac.uk/)
2. Locate the **`POST /auth/request_account`** endpoint.
3. Click **"Try it out"**.
4. Fill in the fields in the form:

- **Username** – your desired username (3–20 characters: letters, numbers, underscores, dots, or dashes).
- **Primary Email** – your main email address. If this is not a workplace email, you must provide additional information in the optional fields to help verify your identity.
- **Professional Email** – optional, use if you have a work email.
- **ORCID** – optional ORCID identifier.
- **Link to Company Profile** – optional link to a public company profile or other identifying information.

**Important:** Users must provide sufficient identifying information, particularly if the primary email is not a workplace email. Insufficient information may result in the account request being rejected.

5. Click **"Execute"** to submit the request.

Once submitted, your account request will be reviewed by an administrator. You will receive an email notification once the account is approved or rejected.

---

## 2. Manage Your Account

Once your account has been approved, you can reset your password, generate new access tokens, and view your account details. The API supports several authentication methods for scripts and CLI:

- **Basic Auth** – username and password in the HTTP header (standard user/password authentication).
- **Bearer Token Auth** – using the token returned from `/auth/new_token`.
- **JSON body** – for endpoints that accept credentials in the body (e.g., `/auth/reset_password`).
- **Query parameters** – for Swagger-generated curl commands.

---

### 2.1 Set a New Password

Endpoint: `/auth/reset_password`

```bash
curl -X POST https://www183.lamp.le.ac.uk/auth/reset_password \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "current_password": "current_password_here",
    "new_password": "new_secure_password_here"
  }'
```

- You must provide your current password to set a new one.
- Passwords should be strong (letters, numbers, symbols).

---

### 2.2 Generate a New Token

Endpoint: `/auth/new_token`

Authenticate using Basic Auth to generate a Bearer token:

```bash
curl -X POST https://www183.lamp.le.ac.uk/auth/new_token \
  -u 'your_username:your_password'
```

Response:

```json
{
  "your_token": "<YOUR_BEARER_TOKEN>",
  "token_type": "Bearer"
}
```

You can now use this token for endpoints that require authentication.

---

### 2.3 View Your Account Details

Endpoint: `/auth/myaccount`

#### a) Standard Basic Auth (user/password)

```bash
curl -v -X POST https://www183.lamp.le.ac.uk/auth/myaccount \
  -u 'your_username:your_password'
```

#### b) Bearer Token

```bash
curl -v -X POST https://www183.lamp.le.ac.uk/auth/myaccount \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>"
```

#### c) JSON body (for endpoints that accept it)

```bash
curl -X POST https://www183.lamp.le.ac.uk/auth/myaccount \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "current_password": "your_password"
  }'
```

#### d) Query parameters (for Swagger cURL)

```bash
curl -X POST "https://www183.lamp.le.ac.uk/auth/myaccount?username=your_username&current_password=your_password"
```

Response:

```json
{
  "access_token": "<YOUR_BEARER_TOKEN>",
  "token_type": "Bearer",
  "expires_in_days": 365
}
```

---

**Notes:**

- The API checks authentication methods in the following order: Bearer token → Basic Auth → JSON body → Query params.
- If you lose your token, reset it via `/auth/reset_password`.
- Keep your tokens and passwords secure. Tokens are valid until they expire, as indicated in `expires_in_days`.

---

## 3 Workflow Endpoint Examples

### 3.1 Curl Examples

- Using Bearer token for a workflow endpoint:

```bash
curl -X POST https://www183.lamp.le.ac.uk/workflow/run_analysis \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -d '{"sample_id": "12345"}'
```

- Using standard username/password Basic Auth for a workflow endpoint:

```bash
curl -X POST https://www183.lamp.le.ac.uk/workflow/run_analysis \
  -u 'your_username:your_password' \
  -d '{"sample_id": "12345"}'
```

### 3.2 Python `requests` Examples

You can also call the workflow endpoints from Python using the `requests` library.

- **Using Bearer Token**

```python
import requests

url = "https://www183.lamp.le.ac.uk/workflow/run_analysis"
headers = {
    "Authorization": "Bearer <YOUR_BEARER_TOKEN>",
    "Content-Type": "application/json"
}
data = {
    "sample_id": "12345"
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json())
```

- **Using Basic Auth (username/password)**

```python
import requests
from requests.auth import HTTPBasicAuth

url = "https://www183.lamp.le.ac.uk/workflow/run_analysis"
data = {
    "sample_id": "12345"
}

response = requests.post(url, auth=HTTPBasicAuth('your_username', 'your_password'), json=data)
print(response.status_code)
print(response.json())
```

**Notes:**

- Make sure to replace `<YOUR_BEARER_TOKEN>` or `'your_username'` / `'your_password'` with your actual credentials.
- `requests` automatically handles HTTPS connections.
- For large workflows or multiple requests, consider using a session to reuse connections:

```python
with requests.Session() as session:
    session.auth = HTTPBasicAuth('your_username', 'your_password')
    response = session.post(url, json=data)
    print(response.json())
```
