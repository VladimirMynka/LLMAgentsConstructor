from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.graph import Graph
from src.db.entities.graph_group import GraphGroup
from src.db.entities.group import Group
from src.db.errors.graph import GraphAlreadyInGroupError, GraphNotFoundError
from src.db.errors.group import GroupNotFoundError, UserNotInGroupError
from src.db.services.member_service import MemberService
from src.db.services.user_service import UserService
from src.models.graph import AddGraphToGroupRequestModel, GraphModel


class GroupGraphService:
    """
    Group of methods for managing group graphs.
    """

    @classmethod
    @use_repository
    def get_group_graphs(
        cls,
        group_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[GraphModel]:
        """
        Get all graphs available for current group.

        Args:
            group_id: int - Group id
            auth_token: str - Authentication token

        Returns:
            list[GraphModel] - List of graphs

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

        graphs: list[Graph] = [relation.graph for relation in group.graphs]

        return [
            GraphModel(
                id=graph.id,
                name=graph.name,
                description=graph.description,
            )
            for graph in graphs
        ]

    @classmethod
    @use_repository
    def add_group_graph(
        cls,
        data: AddGraphToGroupRequestModel,
        group_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[GraphModel]:
        """
        Add graph to group.

        Args:
            data: AddGraphToGroupRequestModel - Add graph to group request model
            group_id: int - Group id
            auth_token: str - Authentication token

        Returns:
            list[GraphModel] - List of graphs

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GroupNotFoundError: If the group is not found
            UserNotInGroupError: If the user is not in the group
            GraphNotFoundError: If the graph is not found
            GraphAlreadyInGroupError: If the graph is already in the group
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        group = repository.get_one(Group, Group.id == group_id)
        if not group:
            raise GroupNotFoundError("Group not found")

        if not MemberService.check_user_in_group(user_model.id, group_id):
            raise UserNotInGroupError("User is not in the group")

        graph = repository.get_one(Graph, Graph.id == data.graph_id)
        if not graph:
            raise GraphNotFoundError("Graph not found")

        if repository.get_one(
            GraphGroup,
            GraphGroup.graph_id == graph.id,
            GraphGroup.group_id == group_id,
        ):
            raise GraphAlreadyInGroupError("Graph already in the group")

        repository.add(GraphGroup(graph_id=graph.id, group_id=group_id))
        repository.commit()

        return cls.get_group_graphs(group_id, auth_token, repository)
