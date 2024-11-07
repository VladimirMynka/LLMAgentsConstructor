import secrets
from datetime import datetime, timedelta
from email.headerregistry import Group
from hashlib import sha256

from pytest import Session

from src.db.decorators import use_repository
from src.db.entities.auth_token import AuthToken
from src.db.entities.user import User
from src.db.errors.user import (
    InvalidCredentialsError,
    NotAuthorizedError,
    UserAlreadyExistsError,
)
from src.models.user import (
    LoginRequestModel,
    LoginResponseModel,
    LogoutResponseModel,
    RegisterRequestModel,
)


class AuthService:
    expiration_days = 30

    @use_repository
    @classmethod
    def register(
        cls, data: RegisterRequestModel, repository: Session
    ) -> LoginResponseModel:
        """
        Register a new user

        Args:
            data: RegisterRequestModel - User data

        Returns:
            LoginResponseModel - User data with auth token
        """
        hashed_password = cls.hash_password(data.password)

        existing_user = repository.get_one(User, User.login == data.username)
        if existing_user:
            raise UserAlreadyExistsError("User already exists")

        new_user = User(login=data.username, password_hash=hashed_password)

        new_group = Group(name=data.username, owner=new_user)

        repository.add(new_user)
        repository.add(new_group)
        repository.commit()
        repository.refresh(new_user)

        return cls._auth_user(new_user, repository)

    @use_repository
    @classmethod
    def login(cls, data: LoginRequestModel, repository: Session) -> LoginResponseModel:
        """
        Login a user

        Args:
            data: LoginRequestModel - User data

        Returns:
            LoginResponseModel - User data with auth token
        """
        hashed_password = cls.hash_password(data.password)

        user = repository.get_one(
            User, User.login == data.username, User.password_hash == hashed_password
        )
        if user is None:
            raise InvalidCredentialsError("Invalid credentials")

        return cls._auth_user(user, repository)

    @use_repository
    @classmethod
    def logout(
        cls,
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

    @classmethod
    def _auth_user(cls, user: User, repository: Session) -> LoginResponseModel:
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
            expiration_date=datetime.now() + timedelta(days=cls.expiration_days),
            user=user,
        )

        repository.add(auth_token)
        repository.commit()
        repository.refresh(auth_token)

        return LoginResponseModel(id=user.id, auth_token=auth_token.token)

    @staticmethod
    def hash_password(password: str) -> str:
        return sha256(password.encode()).hexdigest()
