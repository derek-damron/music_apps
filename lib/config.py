"""Load config and API keys from environment or AWS Secrets Manager."""

import os
from typing import NoReturn

# Load .env when running locally (no effect if file missing or on AWS)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Map service names to env var names
_SERVICE_ENV_KEYS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}


def get_api_key(service_name: str) -> str:
    """
    Return API key for the given service (e.g. 'openai', 'anthropic').
    Reads from environment first; if AWS_SECRET_NAME_FOR_KEYS is set, can
    fall back to Secrets Manager (for Lambda/ECS).
    """
    env_key = _SERVICE_ENV_KEYS.get(service_name.lower())
    if env_key:
        value = os.environ.get(env_key)
        if value:
            return value

    secret_name = os.environ.get("AWS_SECRET_NAME_FOR_KEYS")
    if secret_name:
        return _get_api_key_from_secrets_manager(service_name, secret_name)

    raise _missing_key_error(service_name)


def _get_api_key_from_secrets_manager(service_name: str, secret_name: str) -> str:
    """Fetch API key from AWS Secrets Manager. Cached per process for Lambda."""
    import json
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        raise _missing_key_error(service_name) from None

    client = boto3.client("secretsmanager")
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError:
        raise _missing_key_error(service_name) from None

    secret = response.get("SecretString")
    if not secret:
        raise _missing_key_error(service_name)

    try:
        data = json.loads(secret)
    except json.JSONDecodeError:
        raise _missing_key_error(service_name) from None

    env_key = _SERVICE_ENV_KEYS.get(service_name.lower())
    key_name = env_key or service_name.upper()
    value = data.get(key_name) or data.get(service_name.lower())
    if value:
        return value
    raise _missing_key_error(service_name)


def _missing_key_error(service_name: str) -> NoReturn:
    env_key = _SERVICE_ENV_KEYS.get(service_name.lower(), "API_KEY")
    raise RuntimeError(
        f"Missing API key for {service_name}. "
        f"Set {env_key} in .env or configure AWS_SECRET_NAME_FOR_KEYS."
    )
