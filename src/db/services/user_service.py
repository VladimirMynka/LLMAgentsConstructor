import secrets
from datetime import datetime, timedelta
from hashlib import sha256

from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.auth_token import AuthToken
from src.db.entities.user import User
from src.db.errors.user import (
    InvalidCredentialsError,
    NotAuthorizedError,
    UserAlreadyExistsError,
    UserHasNoPermissionsError,
    UserNotFoundError,
)
from src.models.group import GroupPermissionsModel, UserGroupModel
from src.models.user import (
    ChangePasswordRequestModel,
    ExpandedUserModel,
    GetUserByIdRequestModel,
    LoginRequestModel,
    LoginResponseModel,
    LogoutResponseModel,
    PatchUserModel,
    RegisterRequestModel,
    SearchUserRequestModel,
    UserDetailsModel,
    UserModel,
    UsersModel,
)


class UserService:
    expiration_days = 30

    @use_repository
    def register(
        self, data: RegisterRequestModel, repository: Session
    ) -> LoginResponseModel:
        """
        Register a new user

        Args:
            data: RegisterRequestModel - User data

        Returns:
            LoginResponseModel - User data with auth token
        """
        hashed_password = self._hash_password(data.password)

        existing_user = repository.get_one(User, User.login == data.username)
        if existing_user:
            raise UserAlreadyExistsError("User already exists")

        new_user = User(login=data.username, password_hash=hashed_password)

        repository.add(new_user)
        repository.commit()
        repository.refresh(new_user)

        return self._auth_user(new_user, repository)

    @use_repository
    def login(self, data: LoginRequestModel, repository: Session) -> LoginResponseModel:
        """
        Login a user

        Args:
            data: LoginRequestModel - User data

        Returns:
            LoginResponseModel - User data with auth token
        """
        hashed_password = self._hash_password(data.password)

        user = repository.get_one(
            User, User.login == data.username, User.password_hash == hashed_password
        )
        if user is None:
            raise InvalidCredentialsError("Invalid credentials")

        return self._auth_user(user, repository)

    @use_repository
    def patch_user(
        self, data: PatchUserModel, auth_token: str, repository: Session
    ) -> UserModel:
        """
        Change the login of an existing user

        Args:
            data: PatchUserModel - User data

        Returns:
            UserModel - Updated user data

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            UserAlreadyExistsError: If the new login is already in use
        """
        user = self.get_user_by_auth_token(auth_token, repository)

        existing_user = repository.get_one(User, User.login == data.new_login)
        if existing_user:
            raise UserAlreadyExistsError("Login already in use")

        user.login = data.new_login
        repository.commit()
        repository.refresh(user)

        return UserModel(id=user.id, login=user.login)

    @use_repository
    def change_password(
        self, data: ChangePasswordRequestModel, auth_token: str, repository: Session
    ) -> UserModel:
        """
        Change the password of an existing user.

        Args:
            data: ChangePasswordRequestModel - User data

        Returns:
            UserModel - Updated user data

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            InvalidCredentialsError: If the old password is incorrect
        """
        user = self.get_user_by_auth_token(auth_token, repository)

        hashed_old_password = self._hash_password(data.old_password)

        if user.password_hash != hashed_old_password:
            raise InvalidCredentialsError("Old password is incorrect")

        hashed_new_password = self._hash_password(data.new_password)
        user.password_hash = hashed_new_password

        repository.commit()
        repository.refresh(user)

        return UserModel(id=user.id, login=user.login)

    @use_repository
    def logout(
        self,
        auth_token: str,
        repository: Session,
    ) -> LogoutResponseModel:
        """
        Logout a user

        Args:
            auth_token: str - Authentication token

        Returns:
            LogoutResponseModel - Logout message

        Raises:
            NotAuthorizedError: If the authentication token is invalid
        """
        if not repository.get_one(AuthToken, AuthToken.token == auth_token):
            raise NotAuthorizedError("Authentication token is invalid")

        repository.delete(AuthToken, AuthToken.token == auth_token)
        repository.commit()

        return LogoutResponseModel(message="Logged out")

    @use_repository
    def get_user_by_auth_token(self, auth_token: str, repository: Session) -> UserModel:
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
    def search_users_by_login(
        self,
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
        self.get_user_by_auth_token(auth_token, repository)

        users = repository.query(User).filter(User.login.ilike(f"%{data.query}%")).all()

        return UsersModel(
            users=[UserModel(id=user.id, login=user.login) for user in users]
        )

    @use_repository
    def get_user_by_id(
        self, data: GetUserByIdRequestModel, auth_token: str, repository: Session
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
        request_user = self.get_user_by_auth_token(auth_token, repository)

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
    def get_user_groups(
        self,
        data: GetUserByIdRequestModel,
        auth_token: str,
        repository: Session,
    ) -> list[UserGroupModel]:
        """
        Get user groups.

        Args:
            data: GetUserByIdRequestModel - User id
            auth_token: str - Authentication token

        Returns:
            list[UserGroupModel] - List of user groups

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            UserNotFoundError: If the user is not found
            UserHasNoPermissionsError: If the user has no permissions
        """
        user = repository.get_one(User, User.id == data.user_id)

        if user is None:
            raise UserNotFoundError("User not found")

        request_user = self.get_user_by_auth_token(auth_token, repository)
        if request_user.id != data.user_id:
            raise UserHasNoPermissionsError("User has no permissions")

        return [
            UserGroupModel(
                group_id=user_group.group_id,
                group_name=user_group.group.name,
                permissions=GroupPermissionsModel(
                    owner=user_group.owner,
                    add_users=user_group.add_users,
                    edit_users_permissions=user_group.edit_users_permissions,
                    delete_users=user_group.delete_users,
                    add_graphs=user_group.add_graphs,
                    edit_graphs_permissions=user_group.edit_graphs_permissions,
                    delete_graphs=user_group.delete_graphs,
                ),
            )
            for user_group in user.groups
        ]

    def _auth_user(self, user: User, repository: Session) -> LoginResponseModel:
        """
        Authenticate a user (helper method for login and register)

        Args:
            user: User - User data
            repository: Session - Database session

        Returns:
            LoginResponseModel - User data with auth token
        """
        auth_token = AuthToken(
            token=secrets.token_hex(16),
            expiration_date=datetime.now() + timedelta(days=self.expiration_days),
            user=user,
        )

        repository.add(auth_token)
        repository.commit()
        repository.refresh(auth_token)

        return LoginResponseModel(id=user.id, auth_token=auth_token.token)

    def _hash_password(self, password: str) -> str:
        return sha256(password.encode()).hexdigest()
