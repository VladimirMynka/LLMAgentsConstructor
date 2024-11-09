from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities import AuthToken, User
from src.db.errors.user import (
    InvalidCredentialsError,
    NotAuthorizedError,
    UserAlreadyExistsError,
    UserHasNoPermissionsError,
    UserNotFoundError,
)
from src.db.services.auth_service import AuthService
from src.models.member import GroupPermissionsModel, UserGroupModel
from src.models.user import (
    ChangePasswordRequestModel,
    ExpandedUserModel,
    GetUserByIdRequestModel,
    PatchUserModel,
    SearchUserRequestModel,
    UserDetailsModel,
    UserModel,
    UsersModel,
)


class UserService:
    """
    Group of methods for managing users.
    """

    @use_repository
    @classmethod
    def patch_user(
        cls, data: PatchUserModel, auth_token: str, repository: Session
    ) -> UserModel:
        """
        Change the login of an existing user

        Args:
            data: PatchUserModel - User data
            auth_token: str - Authentication token

        Returns:
            UserModel - Updated user data

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            UserAlreadyExistsError: If the new login is already in use
        """
        user = cls.get_user_by_auth_token(auth_token, repository)

        existing_user = repository.get_one(User, User.login == data.new_login)
        if existing_user:
            raise UserAlreadyExistsError("Login already in use")

        user.login = data.new_login
        repository.commit()
        repository.refresh(user)

        return UserModel(id=user.id, login=user.login)

    @use_repository
    @classmethod
    def change_password(
        cls, data: ChangePasswordRequestModel, auth_token: str, repository: Session
    ) -> UserModel:
        """
        Change the password of an existing user.

        Args:
            data: ChangePasswordRequestModel - User data
            auth_token: str - Authentication token

        Returns:
            UserModel - Updated user data

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            InvalidCredentialsError: If the old password is incorrect
        """
        user = cls.get_user_by_auth_token(auth_token, repository)

        hashed_old_password = AuthService.hash_password(data.old_password)

        if user.password_hash != hashed_old_password:
            raise InvalidCredentialsError("Old password is incorrect")

        hashed_new_password = AuthService.hash_password(data.new_password)
        user.password_hash = hashed_new_password

        repository.commit()
        repository.refresh(user)

        return UserModel(id=user.id, login=user.login)

    @use_repository
    @classmethod
    def get_user_by_auth_token(cls, auth_token: str, repository: Session) -> UserModel:
        """
        Get a user by authentication token.

        Args:
            auth_token: str - Authentication token

        Returns:
            UserModel - User data

        Raises:
            NotAuthorizedError: If the authentication token is invalid
        """
        auth_token = repository.get_one(AuthToken, AuthToken.token == auth_token)
        if not auth_token:
            raise NotAuthorizedError("Authentication token is invalid")

        return UserModel(id=auth_token.user.id, login=auth_token.user.login)

    @use_repository
    @classmethod
    def search_users_by_login(
        cls,
        data: SearchUserRequestModel,
        auth_token: str,
        repository: Session,
    ) -> UsersModel:
        """
        Search users by login.

        Args:
            data: SearchUserRequestModel - Query to search for users
            auth_token: str - Authentication token

        Returns:
            UsersModel - List of matched users

        Raises:
            NotAuthorizedError: If the authentication token is invalid
        """
        cls.get_user_by_auth_token(auth_token, repository)

        users = repository.query(User).filter(User.login.ilike(f"%{data.query}%")).all()

        return UsersModel(
            users=[UserModel(id=user.id, login=user.login) for user in users]
        )

    @use_repository
    @classmethod
    def get_user_by_id(
        cls, data: GetUserByIdRequestModel, auth_token: str, repository: Session
    ) -> ExpandedUserModel:
        """
        Get a user by id.

        Args:
            data: GetUserByIdRequestModel - User id
            auth_token: str - Authentication token

        Returns:
            ExpandedUserModel - User data

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            UserNotFoundError: If the user is not found
        """
        user = repository.get_one(User, User.id == data.user_id)
        request_user = cls.get_user_by_auth_token(auth_token, repository)

        if user is None:
            raise UserNotFoundError("User not found")

        if request_user.id != data.user_id:
            return ExpandedUserModel(user_id=user.id, login=user.login, details=None)

        return ExpandedUserModel(
            user_id=user.id,
            login=user.login,
            details=UserDetailsModel(
                groups_ids=[group.group_id for group in user.groups]
            ),
        )

    @use_repository
    @classmethod
    def get_user_groups(
        cls,
        user_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[UserGroupModel]:
        """
        Get user groups.

        Args:
            user_id: int - User id
            auth_token: str - Authentication token

        Returns:
            list[UserGroupModel] - List of user groups

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            UserNotFoundError: If the user is not found
            UserHasNoPermissionsError: If the user has no permissions
        """
        user = repository.get_one(User, User.id == user_id)

        if user is None:
            raise UserNotFoundError("User not found")

        request_user = cls.get_user_by_auth_token(auth_token, repository)
        if request_user.id != user_id:
            raise UserHasNoPermissionsError("User has no permissions")

        return [
            UserGroupModel(
                group_id=user_group.group_id,
                group_name=user_group.group.name,
                permissions=GroupPermissionsModel(
                    owner=user_group.owner,
                    change_members=user_group.change_members,
                    add_graphs=user_group.add_graphs,
                    run_graphs=user_group.run_graphs,
                    change_graphs_permissions=user_group.change_graphs_permissions,
                    delete_graphs=user_group.delete_graphs,
                ),
            )
            for user_group in user.groups
        ]
