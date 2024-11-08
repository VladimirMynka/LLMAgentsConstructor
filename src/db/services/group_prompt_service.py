from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.group import Group
from src.db.entities.prompt import Prompt
from src.db.entities.prompt_group import PromptGroup
from src.db.errors.group import GroupNotFoundError, UserNotInGroupError
from src.db.errors.prompt import PromptAlreadyInGroupError, PromptNotFoundError
from src.db.services.member_service import MemberService
from src.db.services.user_service import UserService
from src.models.prompt import AddPromptToGroupRequestModel, PromptModel


class GroupPromptService:
    """
    Group of methods for managing group prompts.
    """

    @classmethod
    @use_repository
    def get_group_prompts(
        cls,
        group_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[PromptModel]:
        """
        Get all prompts available for current group.

        Args:
            group_id: int - Group id
            auth_token: str - Authentication token

        Returns:
            list[PromptModel] - List of prompts

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GroupNotFoundError: If the group is not found
            UserNotInGroupError: If the user is not in the group
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        group = repository.get_one(Group, Group.id == group_id)
        if not group:
            raise GroupNotFoundError("Group not found")

        if not MemberService.check_user_in_group(user_model.id, group_id):
            raise UserNotInGroupError("User is not in the group")

        prompts: list[Prompt] = [relation.prompt for relation in group.prompts]

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
    def add_group_prompt(
        cls,
        data: AddPromptToGroupRequestModel,
        group_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[PromptModel]:
        """
        Add prompt to group.

        Args:
            data: AddPromptToGroupRequestModel - Add prompt to group request model
            group_id: int - Group id
            auth_token: str - Authentication token

        Returns:
            list[PromptModel] - List of prompts

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GroupNotFoundError: If the group is not found
            UserNotInGroupError: If the user is not in the group
            PromptNotFoundError: If the prompt is not found
            PromptAlreadyInGroupError: If the prompt is already in the group
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        group = repository.get_one(Group, Group.id == group_id)
        if not group:
            raise GroupNotFoundError("Group not found")

        if not MemberService.check_user_in_group(user_model.id, group_id):
            raise UserNotInGroupError("User is not in the group")

        prompt = repository.get_one(Prompt, Prompt.id == data.prompt_id)
        if not prompt:
            raise PromptNotFoundError("Prompt not found")

        if repository.get_one(
            PromptGroup,
            PromptGroup.prompt_id == prompt.id,
            PromptGroup.group_id == group_id,
        ):
            raise PromptAlreadyInGroupError("Prompt already in the group")

        repository.add(PromptGroup(prompt_id=prompt.id, group_id=group_id))
        repository.commit()

        return cls.get_group_prompts(group_id, auth_token, repository)
