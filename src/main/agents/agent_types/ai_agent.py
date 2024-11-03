import logging

from openai import AsyncOpenAI

from src.main.agents.agent_typings import (
    Document,
    DocumentName,
    DocumentsStore,
    GenerationSettings,
    Message,
    ModelName,
    Role,
)
from src.main.agents.base_agent import BaseAgent


class AIAgent(BaseAgent):
    def __init__(
        self,
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
        **kwargs,
    ):
        """Agent based on LLM."""
        super().__init__(
            name=name,
            documents_store=documents_store,
            input_document_names=input_document_names,
            required_documents=required_documents,
            output_document_name=output_document_name,
            logging_info=logging_info,
            output_document_filename=output_document_filename,
        )
        self._system_prompt: str = system_prompt
        self._client: AsyncOpenAI = client
        role = Role.system if settings.model != ModelName.o1_mini else Role.user
        self._chat: list[Message] = [Message(role, system_prompt)]
        self._settings: GenerationSettings = settings

    async def _run(self) -> None:
        """Run agent and return output document."""
        input_documents = self._documents_store.get_documents(self.input_document_names)
        common_input: str = "\n".join(
            [f"## {doc.name}: \n{doc.content}" for doc in input_documents]
        )

        await self.send(common_input)

    async def send_and_continue(self, message: str, role: Role = Role.user) -> None:
        await self.send(message, role)

    def save_documents(self) -> DocumentsStore:
        """Save documents."""
        last_message = self._chat[-1].content
        result = DocumentsStore(
            {
                self._output_document_name: Document(
                    name=self._output_document_name,
                    content=last_message,
                    filename=self._output_document_filename,
                )
            }
        )
        self._documents_store.update(result)
        return result

    async def send(self, message: str, role: Role = Role.user) -> str | None:
        """Sends message. Returns answer. Save both at chat history."""
        self._chat.append(Message(role, content=message))

        completion = await self._client.chat.completions.create(
            messages=map(Message.to_dict, self._chat),
            **self._settings.to_dict(),
        )
        logging.debug(completion)
        answer = completion.choices[0].message.content

        self._chat.append(Message(Role.assistant, content=answer))

        return answer

    def clear_chat(self) -> None:
        """Clear chat."""
        self._chat = [Message(Role.system, self._system_prompt)]
