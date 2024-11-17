from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.document_template import DocumentTemplate
from src.db.entities.node import Node
from src.db.errors.document_template import (
    DocumentTemplateHasInstancesError,
    DocumentTemplateNotFoundError,
)
from src.db.services.agent_service import AgentService
from src.db.services.graph_service import GraphService
from src.db.services.user_service import UserService
from src.models.agent import AgentModel
from src.models.document import DocumentModel
from src.models.document_template import (
    CreateDocumentTemplateRequestModel,
    ExtendedDocumentTemplateModel,
    UpdateDocumentTemplateRequestModel,
)
from src.models.node import ContentType, NodeModel


class DocumentTemplateService:
    """
    Group of methods for managing document templates.
    """

    @classmethod
    @use_repository
    def get_document_templates(
        cls,
        graph_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[ExtendedDocumentTemplateModel]:
        """
        Get all document templates of the graph.

        Args:
            graph_id: int - Graph id
            auth_token: str - Authentication token
            repository: Session - Database session

        Returns:
            list[ExtendedDocumentTemplateModel] - List of document templates

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        GraphService.check_user_has_access_to_graph(user_model.id, graph_id, repository)

        templates = (
            repository.query(DocumentTemplate)
            .filter(
                DocumentTemplate.node_id.in_(
                    repository.query(Node)
                    .filter(Node.graph_id == graph_id)
                    .with_only_columns(Node.id)
                    .subquery()
                )
            )
            .all()
        )

        return [
            cls._make_document_template_model(template, user_model.id, repository)
            for template in templates
        ]

    @classmethod
    def get_document_template(
        cls,
        template_id: int,
        graph_id: int,
        auth_token: str,
        repository: Session,
    ) -> ExtendedDocumentTemplateModel:
        """
        Get document template by id.

        Args:
            template_id: int - Document template id
            graph_id: int - Graph id
            auth_token: str - Authentication token
            repository: Session - Database session

        Returns:
            ExtendedDocumentTemplateModel - Document template

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
            DocumentTemplateNotFoundError: If the document template is not found
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        GraphService.check_user_has_access_to_graph(user_model.id, graph_id, repository)

        template = repository.get_one(
            DocumentTemplate, DocumentTemplate.id == template_id
        )
        if (not template) or (template.node.graph_id != graph_id):
            raise DocumentTemplateNotFoundError("Document template not found")

        return cls._make_document_template_model(template)

    @classmethod
    @use_repository
    def create_document_template(
        cls,
        graph_id: int,
        data: CreateDocumentTemplateRequestModel,
        auth_token: str,
        repository: Session,
    ) -> list[ExtendedDocumentTemplateModel]:
        """
        Create document template.

        Args:
            graph_id: int - Graph id
            auth_token: str - Authentication token
            data: CreateDocumentTemplateRequestModel - Data
            repository: Session - Database session

        Returns:
            ExtendedDocumentTemplateModel - Document template

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
            AgentNotFoundError: If the agent is not found
        """
        user_model = UserService.get_user_by_auth_token(auth_token)
        GraphService.check_user_has_access_to_graph(user_model.id, graph_id)

        creator = AgentService.get_agent_by_id(data.creator_id, graph_id, auth_token)

        node = Node(
            graph_id=graph_id,
            x=data.node.x,
            y=data.node.y,
        )
        repository.add(node)

        template = DocumentTemplate(
            name=data.name,
            filename=data.name.lower().replace(" ", "_"),
            description=data.description,
            agent=creator,
            node=node,
        )
        repository.add(template)
        repository.commit()

        return cls.get_document_templates(graph_id, auth_token, repository)

    @classmethod
    @use_repository
    def update_document_template(
        cls,
        graph_id: int,
        template_id: int,
        data: UpdateDocumentTemplateRequestModel,
        auth_token: str,
        repository: Session,
    ) -> ExtendedDocumentTemplateModel:
        """
        Update document template.

        Args:
            graph_id: int - Graph id
            template_id: int - Document template id
            data: UpdateDocumentTemplateRequestModel - Data
            auth_token: str - Authentication token
            repository: Session - Database session

        Returns:
            ExtendedDocumentTemplateModel - Document template

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
            DocumentTemplateNotFoundError: If the document template is not found
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        GraphService.check_user_has_access_to_graph(user_model.id, graph_id)

        creator = AgentService.get_agent_by_id(data.creator_id, graph_id, auth_token)

        template = repository.get_one(
            DocumentTemplate, DocumentTemplate.id == template_id
        )
        if (not template) or (template.node.graph_id != graph_id):
            raise DocumentTemplateNotFoundError("Document template not found")

        template.name = data.name
        template.description = data.description
        template.agent = creator

        repository.commit()

        return cls.get_document_templates(graph_id, auth_token, repository)

    @classmethod
    @use_repository
    def delete_document_template(
        cls,
        template_id: int,
        graph_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[ExtendedDocumentTemplateModel]:
        """
        Delete document template.

        Args:
            template_id: int - Document template id
            graph_id: int - Graph id
            auth_token: str - Auth token
            repository: Session - Database session

        Returns:
            list[ExtendedDocumentTemplateModel] - List of document templates

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
            DocumentTemplateNotFoundError: If the document template is not found
            DocumentTemplateHasInstancesError: If the document template has instances
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        GraphService.check_user_has_access_to_graph(user_model.id, graph_id)

        template = repository.get_one(
            DocumentTemplate, DocumentTemplate.id == template_id
        )

        if (not template) or (template.node.graph_id != graph_id):
            raise DocumentTemplateNotFoundError("Document template not found")

        if len(template.instances) > 0:
            raise DocumentTemplateHasInstancesError("Document template has instances")

        node = template.node

        repository.delete(template)
        repository.delete(node)

        repository.commit()

        return cls.get_document_templates(graph_id, auth_token, repository)

    @classmethod
    def _make_document_template_model(
        cls,
        template: DocumentTemplate,
    ) -> ExtendedDocumentTemplateModel:
        """
        Make document template model.
        """
        return ExtendedDocumentTemplateModel(
            id=template.id,
            name=template.name,
            description=template.description,
            creator=AgentModel(
                id=template.agent_id,
                name=template.agent.name,
                agent_type=template.agent.agent_type,
            ),
            node=NodeModel(
                id=template.node_id,
                x=template.node.x,
                y=template.node.y,
                content_type=ContentType.DOCUMENT_TEMPLATE,
            ),
            instances=[
                DocumentModel(
                    id=instance.id,
                )
                for instance in template.instances
            ],
        )
