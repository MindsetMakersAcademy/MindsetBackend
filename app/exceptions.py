from pydantic import ValidationError as PydanticValidationError

__all__ = [
    "ValidationError",
    "PydanticValidationError",
    "DomainError",
    "ConflictError",
    "NotFoundError",
    "AlreadyExistsError",
    "ForbiddenError",
]

class DomainError(Exception): ...

class ValidationError(Exception): ...

class ConflictError(Exception): ...


class NotFoundError(DomainError): ...


class AlreadyExistsError(DomainError): ...


class ForbiddenError(DomainError): ...


