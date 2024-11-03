import asyncio
import logging
from abc import abstractmethod

from src.main.agents.agent_typings import DocumentName, DocumentsStore


class BaseAgent:
    def __init__(
        self,
        name: str,
        documents_store: DocumentsStore,
        input_document_names: list[DocumentName],
        required_documents: list[DocumentName],
        output_document_name: DocumentName | None = None,
        logging_info: tuple[str | None, str | None] = (None, None),
        output_document_filename: str | None = None,
        **kwargs,
    ):
        """Abstract agent to inherit from."""
        self._name: str = name
        self._logging_info: tuple[str | None, str | None] = logging_info
        self._documents_store: DocumentsStore = documents_store
        self._input_document_names: list[DocumentName] = input_document_names
        self._required_documents: list[DocumentName] = required_documents
        self._output_document_name: DocumentName = (
            output_document_name if output_document_name is not None else name
        )
        self._output_document_filename: str | None = output_document_filename

    async def run(self) -> DocumentsStore:
        """Run agent and return output document."""
        while not (
            self._documents_store.contains(self._input_document_names)
            and self._documents_store.contains(self._required_documents)
        ):
            await asyncio.sleep(0.5)

        if self._logging_info[0] is not None:
            logging.info(self._logging_info[0])

        await self._run()

        if self._logging_info[1] is not None:
            logging.info(self._logging_info[1])

        return self.save_documents()

    @abstractmethod
    async def _run(self) -> None:
        """Run agent."""
        raise NotImplementedError

    @abstractmethod
    def save_documents(self) -> DocumentsStore:
        """Save documents."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        """Agent name."""
        return self._name

    @property
    def input_document_names(self) -> set[DocumentName]:
        """Input document names."""
        return set(self._input_document_names)

    @property
    def output_document_names(self) -> set[DocumentName]:
        """Output document names."""
        return set([self._output_document_name])
