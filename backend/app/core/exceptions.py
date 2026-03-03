"""
Custom exception classes for the application.
"""

from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, identifier: str | int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id '{identifier}' not found",
        )


class ValidationException(HTTPException):
    """Raised when validation fails."""

    def __init__(self, message: str, field: str | None = None):
        detail = {"message": message}
        if field:
            detail["field"] = field

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class ServiceException(HTTPException):
    """Raised when a service operation fails."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": message},
        )
