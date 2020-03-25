# <hostname>:<display-id>.<screen-id>
import re

# <hostname>:<display-id>.<screen-id>
HOSTNAME_REGEX = "(localhost|(\d+\.\d+\.\d+\.\d+))"
DISPLAY_ID_REGEX = "\d+"
SCREEN_ID_REGEX = "\d+"
DISPLAY_REGEX = re.compile(
    r"^%s?:%s(\.%s)?$" % (HOSTNAME_REGEX, DISPLAY_ID_REGEX, SCREEN_ID_REGEX)
)

# IDEA: This is currently not used as python-xlib throws a descriptive error
# when handling invalid display IDs. In the event of providing a common error class hierarchy
# is needed, this can be used instead.
def is_valid_display_identifier(display_identifier):
    """
    Checks the format of a Display Identifier.

    Parameters
    ----------
    display_identifier : str
        The display id string to check.

    Returns
    -------
    bool
        Whether this is a valid string or not
    """
    return bool(DISPLAY_REGEX.match(display_identifier))
