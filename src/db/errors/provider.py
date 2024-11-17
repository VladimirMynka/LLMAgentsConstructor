class ProviderNotFoundError(Exception):
    """
    Raised when the provider is not found.
    """

    pass


class UserIsNotProviderOwnerError(Exception):
    """
    Raised when the user is not the owner of the provider.
    """

    pass


class ProviderAlreadyInGroupError(Exception):
    """
    Raised when the provider is already in the group.
    """

    pass


class ProviderTokenNotFoundError(Exception):
    """
    Raised when the provider token is not found.
    """

    pass
