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

## Auth0 setup

See [AUTH0_SETUP.md](AUTH0_SETUP.md) for the first phase of OAuth setup.
