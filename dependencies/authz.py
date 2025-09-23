from dependencies.authn import authenticated_user
from fastapi import Depends, HTTPException, status
from typing import Annotated


def has_roles(roles):
    def check_roles(user: Annotated[any, Depends(authenticated_user)]):
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied!",
            )

    return check_roles
