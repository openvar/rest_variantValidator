# User Signup and Account Guide

This guide will help you create a user account, set your password, and access your account details.

---

## Step 1: Request a User Account

Send a request with your desired username and email:

Visit the Swagger documented endpoint `auth/request_account`

> After submission, your request will be reviewed and approved by an administrator. If we cannot idenntify you, we will not provide access. Refer to (TBC) for guidance

> By requesting an account you are agreeing to our [Terms and Conditions of use](https://github.com/openvar/variantValidator?tab=readme-ov-file#web-services-additional-terms-and-conditions-of-use)

---

## Optional, the following steps can be performed using the Swagger documented endpoints

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
curl -X POST https://www183.lamp.le.ac.uk/auth/reset_password \
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
curl -X POST https://www183.lamp.le.ac.uk/auth/new_token \
  -u 'your-username:your-password'
```

> You can use this token for API requests instead of your password.

---

## Step 4: Access Your Account Details

You can view your account information using **Basic Auth** or a **Bearer Token**.

- **Basic Auth:**

```bash
curl -v -X POST https://www183.lamp.le.ac.uk/auth/myaccount \
  -u 'your-username:your-password'
```

- **Bearer Token Auth:**

```bash
curl -v -X POST https://www183.lamp.le.ac.uk/auth/myaccount \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-generated-token"
```



