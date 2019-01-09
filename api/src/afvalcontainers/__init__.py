"""Afvalcontainer API."""

# API versions (Major, minor, patch)
VERSION = (0, 0, 1)


API_VERSIONS = {
    'v1': (0, 0, 1),
    'suppliers': (0, 0, 1),
}


def get_version(version: tuple = None) -> str:
    """Return version string (x.y[.z]) from given version tuple.

    Note, if no `version` tuple is given we return
    the application version number.

    :param version: version tuple or None
    :returns: version string
    """
    if version is None:
        version = VERSION

    parts = 2 if version[2] == 0 else 3
    return '.'.join(str(v) for v in version[:parts])
