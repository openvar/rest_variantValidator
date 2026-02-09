# User Signup and Account Guide

This guide will help you create a user account, set your password, and access your account details.

---

## Step 1: Request a User Account

Send a request with your desired username and email:

Visit the Swagger documented endpoint `auth/request_account`

> After submission, your request will be reviewed and approved by an administrator. If we cannot identify you, access *will not* be granted. Refer to (TBC) for guidance.

> By requesting an account you are agreeing to our [Terms and Conditions of use](https://github.com/openvar/variantValidator?tab=readme-ov-file#web-services-additional-terms-and-conditions-of-use)

---

## Optional: Perform these steps using the Swagger API

All user endpoints are documented in Swagger. Use the Swagger UI to:

- Request a new account  
- Reset your password  
- Generate a token  
- Retrieve account details  

> The Swagger interface provides a visual, interactive way to try API endpoints without using curl commands. Contact your service administrator for the Swagger URL.

---

## Step 2: Set Your Password

Once approved, set your password using the temporary password provided:

```bash
curl -X POST https://www181.lamp.le.ac.uk/auth/reset_password \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-username",
    "current_password": "temporary-password",
    "new_password": "your-new-password"
  }'
```

> Tip: Choose a secure and memorable password.

---

## Step 3: Generate an Authentication Token

Use your username and password to generate a token:

```bash
curl -X POST https://www181.lamp.le.ac.uk/auth/new_token \
  -u 'your-username:your-password'
```

> You can use this token for API requests instead of your password.

---

## Step 4: Access Your Account Details

You can view your account information using **Basic Auth** or a **Bearer Token**.

- **Basic Auth:**

```bash
curl -v -X POST https://www181.lamp.le.ac.uk/auth/myaccount \
  -u 'your-username:your-password'
```

- **Bearer Token Auth:**

```bash
curl -v -X POST https://www181.lamp.le.ac.uk/auth/myaccount \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-generated-token"
```

---

## Usage Examples

The following examples demonstrate common API usage once authentication has been completed.  
Bearer token authentication is recommended for programmatic access.

---

### VariantValidator endpoint (Validation of all Variant descriptions)
***For genomic variant descriptions, we recommend the LOVD endpoint documented below***

#### Usage guidance

- For optimal performance, set select_transcripts to "mane_select" whenever possible.

- Alternatively, you can provide a specific transcript or list of transcripts relevant to your variants (refer to the Swagger documentation for guidance)

Example variant: `NM_000088.3:c.589G>T`  
Genome build: `GRCh38`

#### curl

```bash
curl -X GET \
  "https://www181.lamp.le.ac.uk/VariantValidator/variantvalidator/GRCh38/NM_000088.3:c.589G>T/all?content-type=application%2Fjson" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-generated-token"
```

#### Python (requests)

```python
import requests

BASE_URL = "https://www181.lamp.le.ac.uk/VariantValidator"
variant = "NM_000088.3:c.589G>T"

url = f"{BASE_URL}/variantvalidator/GRCh38/{variant}/all"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer your-generated-token"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

data = response.json()
print(data)
```

---

### LOVD endpoint (genomic variant descriptions)

#### Usage guidance

- For optimal performance, set select_transcripts to "mane_select" whenever possible.

- Alternatively, you can provide a specific transcript or list of transcripts relevant to your variants (refer to the Swagger documentation for guidance)

Example variant: `chr17:50198002C>A`  
Genome build: `GRCh38`

#### curl

```bash
curl -X GET \
  "https://www181.lamp.le.ac.uk/LOVD/lovd/GRCh38/chr17:50198002C>A/refseq/None/False/False?content-type=application%2Fjson" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-generated-token"
```

#### Python (requests)

```python
import requests

BASE_URL = "https://www181.lamp.le.ac.uk/LOVD/lovd"
variant = "chr17:50198002C>A"

url = f"{BASE_URL}/GRCh38/{variant}/refseq/None/False/False"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer your-generated-token"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

data = response.json()
entry = data[variant]["NC_000017.11:g.50198002C>A"]
print(entry["g_hgvs"])
```

> For full endpoint documentation, parameters, and response schemas, refer to the Swagger UI.
