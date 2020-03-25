class DisplayManagementError(Exception):
    pass


class MalformedInputError(DisplayManagementError):
    pass


class ResourceError(DisplayManagementError):
    pass


class InvalidStateError(DisplayManagementError):
    pass
