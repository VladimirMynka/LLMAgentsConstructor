from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.node import Node
from src.db.errors.node import NodeNotFoundError
from src.db.services.graph_service import GraphService
from src.db.services.user_service import UserService
from src.models.node import ContentType, ExtendedNodeModel
from src.models.prompt import NodeModel, UpdateNodeRequestModel


class NodeService:
    """
    Group of methods for managing nodes.
    """

    @classmethod
    @use_repository
    def get_nodes(
        cls,
        graph_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[NodeModel]:
        """
        Get all nodes of the graph.

        Args:
            graph_id: int - Graph id
            auth_token: str - Authentication token
            repository: Session - Database session

        Returns:
            list[NodeModel] - List of nodes

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        GraphService.check_user_has_access_to_graph(user_model.id, graph_id, repository)

        nodes: list[Node] = (
            repository.query(Node).filter(Node.graph_id == graph_id).all()
        )

        return [
            NodeModel(
                id=node.id,
                x=node.x,
                y=node.y,
                content_type=cls._get_content_type(node),
            )
            for node in nodes
        ]

    @classmethod
    @use_repository
    def get_node_by_id(
        cls,
        graph_id: int,
        node_id: int,
        auth_token: str,
        repository: Session,
    ) -> ExtendedNodeModel:
        """
        Get node by id.

        Args:
            node_id: int - Node id
            auth_token: str - Authentication token

        Returns:
            ExtendedNodeModel - Node

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
            NodeNotFoundError: If the node is not found or user has no access to it
        """
        user_model = UserService.get_user_by_auth_token(auth_token)

        GraphService.check_user_has_access_to_graph(user_model.id, graph_id, repository)

        node = repository.get(Node, node_id)
        if not node:
            raise NodeNotFoundError("Node not found")

        if node.graph_id != graph_id:
            raise NodeNotFoundError("Node not found")

        return ExtendedNodeModel(
            id=node.id,
            x=node.x,
            y=node.y,
            content_type=cls._get_content_type(node),
            content=node.agent or node.document_template,
        )

    @classmethod
    @use_repository
    def move_node(
        cls,
        graph_id: int,
        node_id: int,
        update_node_request: UpdateNodeRequestModel,
        auth_token: str,
        repository: Session,
    ) -> list[NodeModel]:
        """
        Move node to new position.

        Args:
            graph_id: int - Graph id
            node_id: int - Node id
            update_node_request: UpdateNodeRequestModel - Update node request
            auth_token: str - Authentication token
            repository: Session - Database session

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
            NodeNotFoundError: If the node is not found or user has no access to it
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        GraphService.check_user_has_access_to_graph(user_model.id, graph_id, repository)

        node = repository.get(Node, node_id)
        if not node:
            raise NodeNotFoundError("Node not found")

        if node.graph_id != graph_id:
            raise NodeNotFoundError("Node not found")

        node.x = update_node_request.x
        node.y = update_node_request.y

        repository.commit()

        return cls.get_nodes(graph_id, auth_token, repository)

    @staticmethod
    def _get_content_type(node: Node) -> ContentType:
        return ContentType.AGENT if node.agent else ContentType.DOCUMENT
