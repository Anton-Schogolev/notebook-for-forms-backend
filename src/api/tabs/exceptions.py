class TabIdTaken(Exception):
    """Id, provided by the user, isn't unique"""


class TabNotFound(Exception):
    """The requested tab does not exist."""
