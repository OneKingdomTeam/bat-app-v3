from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.model.user import User
from app.service.authentication import (
    jwt_extract_object,
    jwt_to_expiry_status,
    handle_token_renewal,
    user_htmx_dep,
)


router = APIRouter(default_response_class=JSONResponse)

# -------------------------------------------------------------
#       Endpoints
# -------------------------------------------------------------


@router.get("/", name="auth_endpoint")
def get_auth_endpoint():

    return None


@router.get(
    "/token-check", name="auth_token_check_endpoint", response_class=JSONResponse
)
def get_auth_token_refresh(
    request: Request, current_user: User = Depends(user_htmx_dep), renew: int = 0
):

    bearer_token = request.cookies.get("access_token")  # Includes Bearer ...

    if not bearer_token:
        raise HTTPException(status_code=401, detail="Incorect token provided.")

    token_value = bearer_token.split(" ")[1]  # Extracts token string from Bearer ...

    # Check if renewal is requested and token is ready for renewal
    if renew == 1:
        expiry_status = jwt_to_expiry_status(token=token_value)
        if expiry_status == 2:  # Token is ready for renewal (< 180s remaining)
            # Generate new token
            new_bearer_token = handle_token_renewal(current_user=current_user)
            new_token_value = new_bearer_token.split(" ")[1]
            jwt_data = jwt_extract_object(token=new_token_value)

            # Create response with updated token cookie
            response = JSONResponse(content=jwt_data, status_code=200)
            response.set_cookie(
                key="access_token",
                value=new_bearer_token,
                httponly=True,
                secure=True,
                samesite="lax"
            )
            return response

    # Return current token data without renewal
    jwt_data = jwt_extract_object(token=token_value)
    return JSONResponse(content=jwt_data, status_code=200)
