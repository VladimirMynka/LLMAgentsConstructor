from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.graph import Graph
from src.db.entities.graph_group import GraphGroup
from src.db.entities.group import Group
from src.db.entities.user import User
from src.db.entities.user_group import UserGroup
from src.db.errors.graph import GraphNotFoundError, UserIsNotGraphOwnerError
from src.db.errors.user import UserNotFoundError
from src.db.services.user_service import UserService
from src.models.graph import (
    CreateGraphRequestModel,
    ExpandGraphModel,
    GraphModel,
    UpdateGraphRequestModel,
)
from src.models.group import GroupModel


class GraphService:
    """
    Group of methods for managing graphs.
    """

    @classmethod
    @use_repository
    def get_graphs(
        cls,
        auth_token: str,
        repository: Session,
    ) -> list[GraphModel]:
        """
        Get all graphs available for current user.

        Args:
            auth_token: str - Authentication token

        Returns:
            list[GraphModel] - List of graphs

        Raises:
            NotAuthorizedError: If the authentication token is invalid
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        graphs: list[Graph] = cls._get_all_graphs_of_user(user_model.id, repository)

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
    def get_graph_by_id(
        cls,
        graph_id: int,
        auth_token: str,
        repository: Session,
    ) -> ExpandGraphModel:
        """
        Get graph by id.

        Args:
            graph_id: int - Graph id
            auth_token: str - Authentication token

        Returns:
            ExpandGraphModel - Graph

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
        """
        user_model = UserService.get_user_by_auth_token(auth_token)

        cls.check_user_has_access_to_graph(user_model.id, graph_id)

        graph = repository.get(Graph, graph_id)
        if not graph:
            raise GraphNotFoundError("Graph not found")

        return ExpandGraphModel(
            id=graph.id,
            name=graph.name,
            description=graph.description,
            groups=[
                GroupModel(
                    id=graph_group.group_id,
                    name=graph_group.group.name,
                )
                for graph_group in graph.groups
            ],
        )

    @classmethod
    @use_repository
    def create_graph(
        cls,
        graph_model: CreateGraphRequestModel,
        auth_token: str,
        repository: Session,
    ) -> GraphModel:
        """
        Create a new graph.

        Args:
            graph_model: CreateGraphRequestModel - Graph model
            auth_token: str - Authentication token

        Returns:
            GraphModel - Created graph

        Raises:
            NotAuthorizedError: If the authentication token is invalid
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        user: User = repository.get_one(User, User.id == user_model.id)
        base_group: Group = user.base_group

        graph = Graph(
            name=graph_model.name,
            description=graph_model.description,
        )
        repository.add(graph)

        graph_group = GraphGroup(
            graph=graph,
            group=base_group,
        )
        repository.add(graph_group)

        repository.commit()
        repository.refresh(graph)

        return GraphModel(
            id=graph.id,
            name=graph.name,
            description=graph.description,
        )

    @classmethod
    @use_repository
    def update_graph(
        cls,
        graph_id: int,
        graph_model: UpdateGraphRequestModel,
        auth_token: str,
        repository: Session,
    ) -> Graph:
        """
        Update graph by id.

        Args:
            graph_id: int - Graph id
            graph_model: UpdateGraphRequestModel - Graph model
            auth_token: str - Authentication token

        Returns:
            Graph - Updated graph

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
            UserIsNotGraphOwnerError: If the user is not owner of the graph
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        user: User = repository.get_one(User, User.id == user_model.id)
        base_group: Group = user.base_group

        cls.check_user_has_access_to_graph(user_model.id, graph_id)

        graph = repository.get_one(Graph, graph_id)
        if not graph:
            raise GraphNotFoundError("Graph not found")

        graph_group = repository.get_one(
            GraphGroup,
            GraphGroup.graph_id == graph_id,
            GraphGroup.group_id == base_group.id,
        )
        if not graph_group:
            raise UserIsNotGraphOwnerError("User is not owner of this graph")

        graph.name = graph_model.name
        graph.description = graph_model.description

        repository.commit()

        return graph

    @classmethod
    @use_repository
    def delete_graph(
        cls,
        graph_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[GraphModel]:
        """
        Delete graph by id.

        Args:
            graph_id: int - Graph id
            auth_token: str - Authentication token

        Returns:
            list[GraphModel] - List of graphs

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
            UserIsNotGraphOwnerError: If the user is not owner of the graph
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        user: User = repository.get_one(User, User.id == user_model.id)
        base_group: Group = user.base_group

        cls.check_user_has_access_to_graph(user_model.id, graph_id)

        graph = repository.get_one(Graph, graph_id)
        if not graph:
            raise GraphNotFoundError("Graph not found")

        graph_group = repository.get_one(
            GraphGroup,
            GraphGroup.graph_id == graph_id,
            GraphGroup.group_id == base_group.id,
        )
        if not graph_group:
            raise UserIsNotGraphOwnerError("User is not owner of this graph")

        repository.delete(graph)
        repository.commit()

        return cls.get_graphs(auth_token, repository)

    @classmethod
    @use_repository
    def _get_all_graphs_of_user(
        cls,
        user_id: int,
        repository: Session,
    ) -> list[Graph]:
        """
        Get all graphs available for current user.
        """
        user = repository.get_one(User, User.id == user_id)
        if not user:
            raise UserNotFoundError("User not found")

        user_groups: list[UserGroup] = (
            repository.query(UserGroup).filter(UserGroup.user_id == user_id).all()
        )
        groups: list[Group] = [user_group.group for user_group in user_groups]

        graphs: list[Graph] = sum([group.graphs for group in groups], [])

        return graphs

    @classmethod
    @use_repository
    def check_user_has_access_to_graph(
        cls,
        user_id: int,
        graph_id: int,
        repository: Session,
    ):
        """
        Check if the user has access to the graph.

        Args:
            user_id: int - User id
            graph_id: int - Graph id
            repository: Session - Database session

        Raises:
            UserNotFoundError: If the user is not found
            GraphNotFoundError: If the graph is not found
            GraphNotFoundError: If the user has no access to the graph
        """
        user = repository.get_one(User, User.id == user_id)
        if not user:
            raise UserNotFoundError("User not found")

        graph = repository.get_one(Graph, Graph.id == graph_id)
        if not graph:
            raise GraphNotFoundError("Graph not found")

        user_groups: list[UserGroup] = (
            repository.query(UserGroup).filter(UserGroup.user_id == user_id).all()
        )
        groups: list[Group] = [user_group.group for user_group in user_groups]

        if graph not in sum([group.graphs for group in groups], []):
            raise GraphNotFoundError("User has no access to this graph")
