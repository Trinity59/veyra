class VEYRAValidationError(ValueError):
    """Raised when a user-facing value does not satisfy business rules."""


class VEYRABusinessRuleError(RuntimeError):
    """Raised when a workflow violates a business rule."""


class VEYRADatabaseError(RuntimeError):
    """Raised when a database operation fails."""
