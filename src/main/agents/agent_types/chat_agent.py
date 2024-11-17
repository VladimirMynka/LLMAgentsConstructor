from typing import Any, Callable, Coroutine

from openai import AsyncOpenAI

from src.main.agents.agent_typings import (
    Document,
    DocumentName,
    DocumentsStore,
    GenerationSettings,
    Role,
)
from src.main.agents.agent_types.ai_agent import AIAgent


class ChatAgent(AIAgent):
    def __init__(
        self,
        client: AsyncOpenAI,
        name: str,
        system_prompt: str,
        settings: GenerationSettings,
        documents_store: DocumentsStore,
        required_documents: list[DocumentName],
        request_user_message: Callable[[str], Coroutine[Any, Any, str]],
        chat_name: DocumentName,
        last_message_name: DocumentName,
        logging_info: tuple[str | None, str | None] = (None, None),
        last_message_filename: str | None = None,
        chat_filename: str | None = None,
        stop_words: list[str] | None = None,
        **kwargs,
    ):
        """
        AI Agent with chat history and stop words.
        """
        super().__init__(
            client=client,
            documents_store=documents_store,
            input_document_names=[],
            required_documents=required_documents,
            output_document_name=last_message_name,
            name=name,
            system_prompt=system_prompt,
            settings=settings,
            logging_info=logging_info,
            output_document_filename=last_message_filename,
        )
        self._chat_name: str = chat_name
        self._chat_filename: str | None = chat_filename
        self._stop_words: list[str] | None = stop_words
        self._request_user_message: callable[[str], Coroutine[Any, Any, str]] = (
            request_user_message
        )

    async def _run(self) -> None:
        await self.send_and_continue()

    async def send_and_continue(self, message: str | None = None, role: Role = Role.user) -> None:
        await self.send(message, role)
        while not self.stop_me():
            await self.send()

    async def send(self, message: str | None = None, role: Role = Role.user) -> None:
        if message is None:
            if len(self._chat) > 1:
                message = await self._request_user_message(self._chat[-1].content)
            else:
                message = await self._request_user_message("")
        await super().send(message, role)

    def save_documents(self) -> DocumentsStore:
        """
        Save chat to documents store.
        """
        super_result = super().save_documents()

        result = "\n\n".join([str(message) for message in self._chat])
        result = DocumentsStore(
            {
                self._chat_name: Document(
                    name=self._chat_name,
                    content=result,
                    filename=self._chat_filename,
                )
            }
        )

        self._documents_store.update(result)

        return super_result.update(result)

    def stop_me(self) -> bool:
        """
        Check if message contains stop words.
        """
        return any(word in str(self._chat[-1]) for word in self._stop_words)

    @property
    def output_document_names(self) -> set[DocumentName]:
        """Output document names."""
        return set([self._chat_name, self._last_message_name])
