from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.group import Group
from src.db.entities.prompt import Prompt
from src.db.entities.prompt_group import PromptGroup
from src.db.entities.user import User
from src.db.entities.user_group import UserGroup
from src.db.errors.prompt import PromptNotFoundError, UserIsNotPromptOwnerError
from src.db.errors.user import UserNotFoundError
from src.db.services.user_service import UserService
from src.models.group import GroupModel
from src.models.prompt import (
    CreatePromptRequestModel,
    ExpandPromptModel,
    PromptModel,
    UpdatePromptRequestModel,
)


class PromptService:
    """
    Group of methods for managing prompts.
    """

    @classmethod
    @use_repository
    def get_prompts(
        cls,
        auth_token: str,
        repository: Session,
    ) -> list[PromptModel]:
        """
        Get all prompts available for current user.

        Args:
            auth_token: str - Authentication token

        Returns:
            list[PromptModel] - List of prompts

        Raises:
            NotAuthorizedError: If the authentication token is invalid
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        prompts: list[Prompt] = cls._get_all_prompts_of_user(user_model.id, repository)

        return [
            PromptModel(
                id=prompt.id,
                name=prompt.name,
                text=prompt.text,
            )
            for prompt in prompts
        ]

    @classmethod
    @use_repository
    def get_prompt_by_id(
        cls,
        prompt_id: int,
        auth_token: str,
        repository: Session,
    ) -> ExpandPromptModel:
        """
        Get prompt by id.

        Args:
            prompt_id: int - Prompt id
            auth_token: str - Authentication token

        Returns:
            ExpandPromptModel - Prompt

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            PromptNotFoundError: If the prompt is not found or user has no access to it
        """
        user_model = UserService.get_user_by_auth_token(auth_token)

        cls._check_user_has_access_to_prompt(user_model.id, prompt_id)

        prompt = repository.get(Prompt, prompt_id)
        if not prompt:
            raise PromptNotFoundError("Prompt not found")

        return ExpandPromptModel(
            id=prompt.id,
            name=prompt.name,
            text=prompt.text,
            groups=[
                GroupModel(
                    id=prompt_group.group_id,
                    name=prompt_group.group.name,
                )
                for prompt_group in prompt.groups
            ],
        )

    @classmethod
    @use_repository
    def create_prompt(
        cls,
        prompt_model: CreatePromptRequestModel,
        auth_token: str,
        repository: Session,
    ) -> PromptModel:
        """
        Create a new prompt.

        Args:
            prompt_model: CreatePromptRequestModel - Prompt model
            auth_token: str - Authentication token

        Returns:
            PromptModel - Created prompt

        Raises:
            NotAuthorizedError: If the authentication token is invalid
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        user: User = repository.get_one(User, User.id == user_model.id)
        base_group: Group = user.base_group

        prompt = Prompt(
            name=prompt_model.name,
            text=prompt_model.text,
        )
        repository.add(prompt)

        prompt_group = PromptGroup(
            prompt=prompt,
            group=base_group,
        )
        repository.add(prompt_group)

        repository.commit()
        repository.refresh(prompt)

        return PromptModel(
            id=prompt.id,
            name=prompt.name,
            text=prompt.text,
        )

    @classmethod
    @use_repository
    def update_prompt(
        cls,
        prompt_id: int,
        prompt_model: UpdatePromptRequestModel,
        auth_token: str,
        repository: Session,
    ) -> Prompt:
        """
        Update prompt by id.

        Args:
            prompt_id: int - Prompt id
            prompt_model: UpdatePromptRequestModel - Prompt model
            auth_token: str - Authentication token

        Returns:
            Prompt - Updated prompt

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            PromptNotFoundError: If the prompt is not found or user has no access to it
            UserIsNotPromptOwnerError: If the user is not owner of the prompt
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        user: User = repository.get_one(User, User.id == user_model.id)
        base_group: Group = user.base_group

        cls._check_user_has_access_to_prompt(user_model.id, prompt_id)

        prompt = repository.get_one(Prompt, prompt_id)
        if not prompt:
            raise PromptNotFoundError("Prompt not found")

        prompt_group = repository.get_one(
            PromptGroup,
            PromptGroup.prompt_id == prompt_id,
            PromptGroup.group_id == base_group.id,
        )
        if not prompt_group:
            raise UserIsNotPromptOwnerError("User is not owner of this prompt")

        prompt.name = prompt_model.name
        prompt.text = prompt_model.text

        repository.commit()

        return prompt

    @classmethod
    @use_repository
    def delete_prompt(
        cls,
        prompt_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[PromptModel]:
        """
        Delete prompt by id.

        Args:
            prompt_id: int - Prompt id
            auth_token: str - Authentication token

        Returns:
            list[PromptModel] - List of prompts

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            PromptNotFoundError: If the prompt is not found or user has no access to it
            UserIsNotPromptOwnerError: If the user is not owner of the prompt
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        user: User = repository.get_one(User, User.id == user_model.id)
        base_group: Group = user.base_group

        cls._check_user_has_access_to_prompt(user_model.id, prompt_id)

        prompt = repository.get_one(Prompt, prompt_id)
        if not prompt:
            raise PromptNotFoundError("Prompt not found")

        prompt_group = repository.get_one(
            PromptGroup,
            PromptGroup.prompt_id == prompt_id,
            PromptGroup.group_id == base_group.id,
        )
        if not prompt_group:
            raise UserIsNotPromptOwnerError("User is not owner of this prompt")

        repository.delete(prompt)
        repository.commit()

        return cls.get_prompts(auth_token, repository)

    @classmethod
    @use_repository
    def _get_all_prompts_of_user(
        cls,
        user_id: int,
        repository: Session,
    ) -> list[Prompt]:
        """
        Get all prompts available for current user.
        """
        user = repository.get_one(User, User.id == user_id)
        if not user:
            raise UserNotFoundError("User not found")

        user_groups: list[UserGroup] = (
            repository.query(UserGroup).filter(UserGroup.user_id == user_id).all()
        )
        groups: list[Group] = [user_group.group for user_group in user_groups]

        prompts: list[Prompt] = sum([group.prompts for group in groups], [])

        return prompts

    @classmethod
    @use_repository
    def _check_user_has_access_to_prompt(
        cls,
        user_id: int,
        prompt_id: int,
        repository: Session,
    ):
        """
        Check if the user has access to the prompt.
        """
        user = repository.get_one(User, User.id == user_id)
        if not user:
            raise UserNotFoundError("User not found")

        prompt = repository.get_one(Prompt, Prompt.id == prompt_id)
        if not prompt:
            raise PromptNotFoundError("Prompt not found")

        user_groups: list[UserGroup] = (
            repository.query(UserGroup).filter(UserGroup.user_id == user_id).all()
        )
        groups: list[Group] = [user_group.group for user_group in user_groups]

        if prompt not in sum([group.prompts for group in groups], []):
            raise PromptNotFoundError("User has no access to this prompt")

    @staticmethod
    def get_prompt_model(prompt: Prompt) -> PromptModel:
        """
        Get prompt model.
        """
        return PromptModel(
            id=prompt.id,
            name=prompt.name,
            text=prompt.text,
        )
