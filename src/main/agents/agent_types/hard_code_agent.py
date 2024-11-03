from typing import Callable, TypeAlias

from src.main.agents.agent_typings import Document, DocumentName, DocumentsStore
from src.main.agents.base_agent import BaseAgent

HardCodeLogic: TypeAlias = Callable[[str], str]


class HardCodeAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        documents_store: DocumentsStore,
        input_document_names: list[DocumentName],
        required_documents: list[DocumentName],
        output_document_name: DocumentName,
        hard_code_logic: HardCodeLogic,
        logging_info: tuple[str | None, str | None] = (None, None),
        output_document_filename: str | None = None,
        **kwargs,
    ):
        """Agent with hard-coded logic."""
        super().__init__(
            name=name,
            documents_store=documents_store,
            input_document_names=input_document_names,
            required_documents=required_documents,
            output_document_name=output_document_name,
            logging_info=logging_info,
            output_document_filename=output_document_filename,
        )
        self._hard_code_logic: HardCodeLogic = hard_code_logic
        self._last_result: str | None = None

    async def _run(self) -> None:
        """Run agent."""
        input_documents = self._documents_store.get_documents(
            self._input_document_names
        )
        input_content = "\n".join([doc.content for doc in input_documents])
        self._last_result = self._hard_code_logic(input_content)

    def save_documents(self) -> DocumentsStore:
        """Save documents."""
        document = Document(
            name=self._output_document_name,
            content=self._last_result,
            filename=self._output_document_filename,
        )
        store = DocumentsStore({self._output_document_name: document})
        self._documents_store.update(store)
        return store
