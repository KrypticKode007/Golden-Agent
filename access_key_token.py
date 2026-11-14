import os
import hmac
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials

ACCESS_KEY_TOKEN: str = os.getenv("ACCESS_KEY_TOKEN", "")

api_key_header = APIKeyHeader(name="X-Access-Key-Token", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def verify_access_key_token(
    header_token: str = Security(api_key_header),
    bearer_creds: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    active_token = os.getenv("ACCESS_KEY_TOKEN", ACCESS_KEY_TOKEN)

    if not active_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ACCESS_KEY_TOKEN is blank. Set ACCESS_KEY_TOKEN in your environment to unlock access.",
        )

    provided_token = header_token or (bearer_creds.credentials if bearer_creds else "")

    if not provided_token or not hmac.compare_digest(provided_token, active_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Access Key Token.",
        )

    return provided_token
