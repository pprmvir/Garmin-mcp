# Garmin MCP Server

An MCP server that provides read-only access to Garmin Personal API activity,
sleep, HRV, user-summary, and wellness data.

## Local setup

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file containing your Garmin Personal API key:

```text
GARMIN_PERSONAL_API_KEY=your-personal-api-key
```

Configure the Auth0 variables described in [Setting up Auth](#setting-up-auth)
before starting the server. The Garmin key alone is not sufficient.

Run the server locally:

```bash
python server.py
```

The Streamable HTTP MCP endpoint is available at:

```text
http://127.0.0.1:8000/mcp
```

## Run tests

Run the full unit-test suite from the project root:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

If the virtual environment is active, this is equivalent:

```bash
python -m unittest discover -s tests -v
```

The tests do not call Garmin or require a real Garmin API key. They cover
Garmin request construction, input validation, token caching and retry logic,
and Auth0 configuration validation.

## Setting up Auth

Auth0 issues access tokens that ChatGPT sends to this server. The server checks
the token's signature, issuer, audience, expiration, and `read:garmin` scope
before allowing access to Garmin tools.

### 1. Create an Auth0 tenant

Create an account at [Auth0](https://auth0.com/) and create a tenant. Record the
**Domain** from your application settings, such as `dev-example.us.auth0.com`.
Google can be used as a sign-in connection through Auth0; enable it for the
application if you want Google login.

### 2. Register the Garmin API

In **Applications → APIs → Create API**, enter:

| Setting | Value |
| --- | --- |
| Name | Garmin MCP API |
| Identifier | Your exact public MCP URL, including `/mcp` |
| Signing algorithm | RS256 |

For our deployment, the Identifier is:

```text
https://garmin-mcp-fl46.onrender.com/mcp
```

Under **Permissions**, add `read:garmin` with the description
`Read Garmin wellness and activity data`.

### 3. Register the ChatGPT OAuth application

In **Applications → Applications → Create Application**, choose **Regular Web
Application** and give it a name such as `ChatGPT Garmin MCP`. Keep the
Authorization Code grant enabled. Record its **Client ID** and **Client Secret**
for the ChatGPT connection. The Client ID is different from the tenant Domain.

The Python Quickstart is optional; this project already implements token
verification. Its generated Render `/callback` URL is not the ChatGPT callback.

### 4. Grant the application API access

Open **Applications → APIs → Garmin MCP API → Settings**. Keep
**User-delegated Access** set to **Per-app authorization**.

Under **Application Access**, select your OAuth application and edit its
**User-Delegated Access**. Grant `read:garmin` and save. Leave the application's
**Client Access** unauthorized and third-party default permissions unauthorized.
If the permission list is empty, first add `read:garmin` in the API's
**Permissions** tab.

### 5. Configure the server and deploy

Set these variables in Render's **Environment** page and in your local `.env`
when running locally:

```text
GARMIN_PERSONAL_API_KEY=<your Garmin Personal API key>
AUTH0_DOMAIN=<your tenant domain, without https:// or a trailing slash>
MCP_SERVER_URL=https://garmin-mcp-fl46.onrender.com/mcp
AUTH0_AUDIENCE=https://garmin-mcp-fl46.onrender.com/mcp
AUTH0_REQUIRED_SCOPE=read:garmin
```

For another deployment, replace both URLs with its own public MCP URL. Copy the
hostname directly from Render: `fl46` contains a lowercase `l`, not the digit
`1`. The Auth0 API Identifier, `AUTH0_AUDIENCE`, and `MCP_SERVER_URL` must match
exactly, including the path and trailing slash convention.

Keep `.env` untracked. The Auth0 Client Secret belongs in ChatGPT's OAuth setup;
the MCP server does not need it. Deploy the authentication code and save the
Render environment changes before connecting ChatGPT.

### 6. Connect ChatGPT

1. In ChatGPT, add a custom MCP server with your public `/mcp` URL and select
   **OAuth** authentication.
2. Choose **User-Defined OAuth Client**, then enter the Auth0 application's
   **Client ID** and **Client Secret**.
3. Copy the exact **Callback URL** displayed by ChatGPT. In Auth0, open that
   application's **Settings → Allowed Callback URLs**, add the URL, and save.
   Use the displayed value rather than guessing a callback address.
4. If ChatGPT asks for default scopes, include `read:garmin`.
5. Accept the custom server acknowledgment, create the connection, and complete
   Auth0 sign-in.
6. Ask ChatGPT to retrieve your recent Garmin activities to verify access.

### 7. Verify and troubleshoot

An anonymous request to `/mcp` should return **401 Unauthorized**. The public
discovery endpoint should return JSON describing the resource and Auth0 issuer:

```text
https://garmin-mcp-fl46.onrender.com/.well-known/oauth-protected-resource/mcp
```

| Symptom | What to check |
| --- | --- |
| `Unknown client` in Auth0 | ChatGPT must use the application's Client ID, not the tenant Domain. |
| Discovery fails or Render returns `x-render-routing: no-server` | Copy the exact service hostname from Render. |
| Authentication succeeds but tool discovery fails | Inspect Render logs for token verification errors; compare API Identifier and audience, issuer, and requested scope. |
| `403` due to insufficient scope | Grant the application `read:garmin` and request that scope in ChatGPT. |

After changing OAuth configuration, reconnect ChatGPT to obtain a fresh token.

Each deployment currently uses one Garmin API key. Authentication does not
automatically map an Auth0 user to a Garmin account. A restriction to a specific
Auth0 user is not currently implemented; configure explicit user authorization
before treating the deployment as accessible only to its owner.
