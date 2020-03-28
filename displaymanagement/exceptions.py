class DisplayManagementError(Exception):
    pass


class MalformedInputError(DisplayManagementError):
    """Thrown when a method is provided with arguments that are not within the allowed set"""

    pass


class ResourceError(DisplayManagementError):
    """Thrown when a method invocation requires an illegal access to some underlying resource"""

    pass


class InvalidStateError(DisplayManagementError):
    """Thrown when a method invocation effect is not defined for the current state of the object"""

    pass
