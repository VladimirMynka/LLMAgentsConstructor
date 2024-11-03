class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class UserHasNoPermissionsError(Exception):
    pass


class NotAuthorizedError(Exception):
    pass

