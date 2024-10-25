from openai import AsyncOpenAI

from src.core.agents.agent_typings import (
    Document,
    DocumentName,
    DocumentsStore,
    GenerationSettings,
    ModelName,
    Role,
)
from src.core.agents.agent_types.ai_agent import AIAgent


class CriticAgent(AIAgent):
    def __init__(
        self,
        criticized_agent: AIAgent,
        client: AsyncOpenAI,
        name: str,
        system_prompt: str,
        settings: GenerationSettings,
        documents_store: DocumentsStore,
        input_document_names: list[DocumentName],
        required_documents: list[DocumentName],
        output_document_name: DocumentName | None = None,
        logging_info: tuple[str | None, str | None] = (None, None),
        output_document_filename: str | None = None,
        max_iterations: int = 10,
        **kwargs,
    ):
        """
        Agent for criticizing another agent.
        """
        super().__init__(
            client=client,
            documents_store=documents_store,
            input_document_names=input_document_names,
            required_documents=required_documents,
            output_document_name=output_document_name,
            name=name,
            system_prompt=system_prompt,
            settings=settings,
            logging_info=logging_info,
            output_document_filename=output_document_filename,
        )
        self._criticized_agent: AIAgent = criticized_agent
        self._saving_critics: list[str] = []
        self._max_iterations: int = max_iterations

    async def _run(self) -> DocumentsStore:
        """
        Run agent and return output document.
        """

        i = 0

        input_documents = self._documents_store.get_documents(
            self._input_document_names
        )
        critics = await self.send(
            "\n\n".join([str(document) for document in input_documents])
        )
        self._saving_critics.append(f"Critics {i}: {critics}")

        while "OK" not in critics:
            i += 1

            # TODO: remove it when o1-mini will be fixed
            role = (
                Role.system
                if self._criticized_agent._settings.model != ModelName.o1_mini
                else Role.user
            )
            await self._criticized_agent.send(critics, role=role)
            self._criticized_agent.save_documents()
            input_documents = self._documents_store.get_documents(
                self._input_document_names
            )
            critics = await self.send(
                "\n\n".join([str(document) for document in input_documents])
            )
            self._saving_critics.append(f"Critics {i}: {critics}")

            if i > self._max_iterations:
                break

        return self.save_documents()

    def save_documents(self) -> DocumentsStore:
        """Save documents."""
        result = "\n\n".join(self._saving_critics)
        result = DocumentsStore(
            {
                self._output_document_name: Document(
                    name=self._output_document_name,
                    content=result,
                    filename=self._output_document_filename,
                )
            }
        )
        self._documents_store.update(result)
        return result
